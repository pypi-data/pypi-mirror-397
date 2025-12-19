"""
MITRE ATT&CK Detection Query - Compatible Version

Works with different versions of mitreattack-python library.
Uses your local MITRE data from mitre-mcp-server.

Installation:
    pip install stix2

Usage:
    python detection_query_compatible.py
"""

import os
import json
from pathlib import Path
from stix2 import MemoryStore, Filter


def find_mitre_data_path():
    """Find the local MITRE data path from mitre-mcp-server."""
    
    possible_paths = [
        "./src/mitre_mcp_server/data/v18.1/enterprise-attack.json",
        "../src/mitre_mcp_server/data/v18.1/enterprise-attack.json",
        os.path.expanduser("~/.mitre-mcp-server/data/enterprise-attack.json"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found local MITRE data at: {path}\n")
            return path
    
    return None


def load_attack_data(data_path):
    """Load MITRE ATT&CK data from JSON file."""
    print(f"📥 Loading data from: {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a STIX memory store
    store = MemoryStore(stix_data=data['objects'])
    
    print(f"✅ Loaded {len(data['objects'])} STIX objects\n")
    
    return store


def get_technique_by_id(store, technique_id):
    """Get a technique object by its ATT&CK ID."""
    
    # Query for attack-pattern with matching external ID
    techniques = store.query([
        Filter("type", "=", "attack-pattern"),
    ])
    
    for tech in techniques:
        if hasattr(tech, 'external_references'):
            for ref in tech.external_references:
                if ref.get('source_name') == 'mitre-attack' and ref.get('external_id') == technique_id:
                    return tech
    
    return None


def get_detection_info(technique_id, data_path=None):
    """
    Get detection information for a MITRE ATT&CK technique.
    
    Args:
        technique_id: Technique ID like "T1055" or "T1059.001"
        data_path: Path to local enterprise-attack.json file
    """
    print(f"\n{'='*80}")
    print(f"🔍 Querying {technique_id}...")
    print(f"{'='*80}\n")
    
    # Find data path if not provided
    if not data_path:
        data_path = find_mitre_data_path()
        if not data_path:
            print("❌ Could not find local MITRE data.")
            return None
    
    # Load data
    store = load_attack_data(data_path)
    
    # Get technique
    technique = get_technique_by_id(store, technique_id)
    
    if not technique:
        print(f"❌ Technique {technique_id} not found")
        return None
    
    # Print basic info
    tech_name = technique.name if hasattr(technique, 'name') else technique.get('name')
    tech_id = technique.id if hasattr(technique, 'id') else technique.get('id')
    
    print(f"🎯 {technique_id}: {tech_name}")
    print(f"STIX ID: {tech_id}")
    print(f"{'='*80}\n")
    
    # Get detection guidance
    detection_text = getattr(technique, 'x_mitre_detection', None) if hasattr(technique, '__dict__') else technique.get('x_mitre_detection')
    
    if detection_text:
        print(f"📋 Detection Guidance:")
        print(f"{'-'*80}")
        if len(detection_text) > 500:
            print(f"{detection_text[:500]}...")
            print(f"\n[Full text is {len(detection_text)} characters]")
        else:
            print(f"{detection_text}")
        print()
    else:
        print(f"⚠️  No detection guidance available\n")
    
    # Get data components that detect this technique
    print(f"🔍 Data Components for Detection:")
    print(f"{'-'*80}")
    
    # Find relationships where something "detects" this technique
    relationships = store.query([
        Filter("type", "=", "relationship"),
        Filter("relationship_type", "=", "detects"),
        Filter("target_ref", "=", tech_id)
    ])
    
    if not relationships:
        print("  ⚠️  No data components found for this technique\n")
        return {
            "technique_id": technique_id,
            "name": technique.name,
            "detection": detection_text,
            "data_components": []
        }
    
    print(f"  Found {len(relationships)} detection method(s):\n")
    
    detection_methods = []
    
    for rel in relationships:
        # Get the data component
        source_ref = rel.source_ref if hasattr(rel, 'source_ref') else rel.get('source_ref')
        
        data_components = store.query([
            Filter("id", "=", source_ref)
        ])
        
        if data_components:
            component = data_components[0]
            
            # Handle both dict and object formats
            if isinstance(component, dict):
                component_name = component.get('name')
                data_source_ref = component.get('x_mitre_data_source_ref')
            else:
                component_name = component.name
                data_source_ref = getattr(component, 'x_mitre_data_source_ref', None)
            
            # Get parent data source
            if data_source_ref:
                data_sources = store.query([
                    Filter("id", "=", data_source_ref)
                ])
                
                if data_sources:
                    ds = data_sources[0]
                    data_source_name = ds.get('name') if isinstance(ds, dict) else ds.name
                else:
                    data_source_name = "Unknown"
            else:
                data_source_name = "Unknown"
            
            description = rel.description if hasattr(rel, 'description') else rel.get('description', "No description")
            
            detection_methods.append({
                "data_source": data_source_name,
                "data_component": component_name,
                "description": description
            })
            
            print(f"  • {data_source_name}: {component_name}")
            
            # Print description
            if description and description != "No description":
                if len(description) > 150:
                    print(f"    → {description[:150]}...")
                else:
                    print(f"    → {description}")
            print()
    
    return {
        "technique_id": technique_id,
        "name": tech_name,
        "detection": detection_text,
        "data_components": detection_methods
    }


def list_all_data_sources(data_path=None):
    """List all available data sources in MITRE ATT&CK."""
    
    if not data_path:
        data_path = find_mitre_data_path()
        if not data_path:
            print("❌ Could not find local MITRE data.")
            return
    
    print(f"\n{'='*80}")
    print(f"📊 Loading Data Sources...")
    print(f"{'='*80}\n")
    
    store = load_attack_data(data_path)
    
    # Get all data sources
    data_sources = store.query([
        Filter("type", "=", "x-mitre-data-source")
    ])
    
    print(f"Found {len(data_sources)} data sources:\n")
    
    # Sort by name
    sorted_sources = sorted(data_sources, key=lambda x: x.get('name') if isinstance(x, dict) else x.name)
    
    for ds in sorted_sources[:15]:  # Show first 15
        ds_name = ds.get('name') if isinstance(ds, dict) else ds.name
        ds_id = ds.get('id') if isinstance(ds, dict) else ds.id
        
        # Get components for this data source
        components = store.query([
            Filter("type", "=", "x-mitre-data-component"),
            Filter("x_mitre_data_source_ref", "=", ds_id)
        ])
        
        print(f"  • {ds_name} ({len(components)} components)")
        
        # Show first 3 components
        for comp in components[:3]:
            comp_name = comp.get('name') if isinstance(comp, dict) else comp.name
            print(f"    - {comp_name}")
        
        if len(components) > 3:
            print(f"    ... and {len(components) - 3} more")
        print()
    
    if len(data_sources) > 15:
        print(f"... and {len(data_sources) - 15} more data sources")


def find_techniques_by_data_component(component_keyword, data_path=None):
    """Find techniques that can be detected by a data component."""
    
    if not data_path:
        data_path = find_mitre_data_path()
        if not data_path:
            print("❌ Could not find local MITRE data.")
            return
    
    print(f"\n{'='*80}")
    print(f"🔎 Finding techniques detected by components matching '{component_keyword}'")
    print(f"{'='*80}\n")
    
    store = load_attack_data(data_path)
    
    # Get all data components
    all_components = store.query([
        Filter("type", "=", "x-mitre-data-component")
    ])
    
    # Find matching components
    matches = [
        c for c in all_components
        if component_keyword.lower() in (c.get('name') if isinstance(c, dict) else c.name).lower()
    ]
    
    if not matches:
        print(f"❌ No data components found matching '{component_keyword}'")
        return
    
    print(f"Found {len(matches)} matching component(s):\n")
    
    for component in matches[:3]:  # Show first 3 matches
        comp_name = component.get('name') if isinstance(component, dict) else component.name
        comp_id = component.get('id') if isinstance(component, dict) else component.id
        
        # Get parent data source
        data_source_ref = component.get('x_mitre_data_source_ref') if isinstance(component, dict) else getattr(component, 'x_mitre_data_source_ref', None)
        
        if data_source_ref:
            data_sources = store.query([
                Filter("id", "=", data_source_ref)
            ])
            if data_sources:
                ds = data_sources[0]
                data_source_name = ds.get('name') if isinstance(ds, dict) else ds.name
            else:
                data_source_name = "Unknown"
        else:
            data_source_name = "Unknown"
        
        print(f"📌 {data_source_name}: {comp_name}")
        print(f"{'-'*80}")
        
        # Get techniques detected by this component
        relationships = store.query([
            Filter("type", "=", "relationship"),
            Filter("relationship_type", "=", "detects"),
            Filter("source_ref", "=", comp_id)
        ])
        
        if not relationships:
            print("  No techniques found\n")
            continue
        
        print(f"  Detects {len(relationships)} technique(s):")
        
        for rel in relationships[:10]:  # Show first 10
            # Get the technique
            rel_target = rel.get('target_ref') if isinstance(rel, dict) else rel.target_ref
            
            techniques = store.query([
                Filter("id", "=", rel_target)
            ])
            
            if techniques:
                technique = techniques[0]
                tech_name = technique.get('name') if isinstance(technique, dict) else technique.name
                
                # Get ATT&CK ID
                attack_id = "Unknown"
                ext_refs = technique.get('external_references') if isinstance(technique, dict) else getattr(technique, 'external_references', [])
                
                if ext_refs:
                    for ref in ext_refs:
                        ref_dict = ref if isinstance(ref, dict) else ref.__dict__
                        if ref_dict.get('source_name') == 'mitre-attack':
                            attack_id = ref_dict.get('external_id', 'Unknown')
                            break
                
                print(f"    • {attack_id}: {tech_name}")
        
        if len(relationships) > 10:
            print(f"    ... and {len(relationships) - 10} more")
        
        print()


def analyze_detection_coverage(technique_ids, data_path=None):
    """Analyze detection coverage for a list of techniques."""
    
    if not data_path:
        data_path = find_mitre_data_path()
        if not data_path:
            print("❌ Could not find local MITRE data.")
            return
    
    print(f"\n{'='*80}")
    print(f"📊 DETECTION COVERAGE ANALYSIS")
    print(f"{'='*80}\n")
    
    store = load_attack_data(data_path)
    
    coverage_report = []
    
    for tech_id in technique_ids:
        technique = get_technique_by_id(store, tech_id)
        
        if not technique:
            print(f"⚠️  Technique {tech_id} not found")
            continue
        
        tech_name = technique.get('name') if isinstance(technique, dict) else technique.name
        tech_stix_id = technique.get('id') if isinstance(technique, dict) else technique.id
        
        # Get data components
        relationships = store.query([
            Filter("type", "=", "relationship"),
            Filter("relationship_type", "=", "detects"),
            Filter("target_ref", "=", tech_stix_id)
        ])
        
        # Extract unique data sources
        data_sources = set()
        for rel in relationships:
            rel_source = rel.get('source_ref') if isinstance(rel, dict) else rel.source_ref
            
            components = store.query([
                Filter("id", "=", rel_source)
            ])
            
            if components:
                comp = components[0]
                ds_ref = comp.get('x_mitre_data_source_ref') if isinstance(comp, dict) else getattr(comp, 'x_mitre_data_source_ref', None)
                
                if ds_ref:
                    ds_objs = store.query([
                        Filter("id", "=", ds_ref)
                    ])
                    if ds_objs:
                        ds = ds_objs[0]
                        ds_name = ds.get('name') if isinstance(ds, dict) else ds.name
                        data_sources.add(ds_name)
        
        detection_text = technique.get('x_mitre_detection') if isinstance(technique, dict) else getattr(technique, 'x_mitre_detection', None)
        
        coverage_report.append({
            "technique_id": tech_id,
            "technique_name": tech_name,
            "data_component_count": len(relationships),
            "data_sources": list(data_sources),
            "has_detection_guidance": bool(detection_text and detection_text.strip()),
        })
    
    # Print reports
    print(f"Analyzed {len(coverage_report)} techniques:\n")
    
    for item in coverage_report:
        print(f"{'='*80}")
        print(f"{item['technique_id']}: {item['technique_name']}")
        print(f"{'='*80}")
        print(f"  Data Sources Required: {', '.join(item['data_sources']) or 'None'}")
        print(f"  Data Components: {item['data_component_count']}")
        print(f"  Detection Guidance: {'✅ Yes' if item['has_detection_guidance'] else '❌ No'}")
        print()
    
    # Summary
    if coverage_report:
        avg_components = sum(r['data_component_count'] for r in coverage_report) / len(coverage_report)
        with_guidance = sum(1 for r in coverage_report if r['has_detection_guidance'])
        
        print(f"{'='*80}")
        print(f"📊 Summary:")
        print(f"{'='*80}")
        print(f"  Average data components per technique: {avg_components:.1f}")
        print(f"  Techniques with detection guidance: {with_guidance}/{len(coverage_report)}")
        print()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n🎯 MITRE ATT&CK Detection Query Tool (Compatible Version)\n")
    
    # Auto-detect data path
    DATA_PATH = None
    
    print("="*80)
    print("Example 1: Get detection info for T1055 (Process Injection)")
    print("="*80)
    get_detection_info("T1055", data_path=DATA_PATH)
    
    print("\n" + "="*80)
    print("Example 2: Get detection info for T1059.001 (PowerShell)")
    print("="*80)
    get_detection_info("T1059.001", data_path=DATA_PATH)
    
    print("\n" + "="*80)
    print("Example 3: List data sources")
    print("="*80)
    list_all_data_sources(data_path=DATA_PATH)
    
    print("\n" + "="*80)
    print("Example 4: Find techniques detected by 'Process Creation'")
    print("="*80)
    find_techniques_by_data_component("Process Creation", data_path=DATA_PATH)
    
    print("\n" + "="*80)
    print("Example 5: Detection coverage analysis")
    print("="*80)
    sample_techniques = ["T1055", "T1059.001", "T1053.005", "T1218.011"]
    analyze_detection_coverage(sample_techniques, data_path=DATA_PATH)
    
    print("\n✅ All examples complete!\n")