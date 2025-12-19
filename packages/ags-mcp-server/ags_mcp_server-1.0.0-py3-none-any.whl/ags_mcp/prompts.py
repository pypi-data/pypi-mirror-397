"""MCP prompts - guided workflows and best practices for Anzo tools."""

def register_prompts(mcp):
    """Register MCP prompts to guide the agent."""
    
    @mcp.prompt()
    def knowledge_graph_linking_overview() -> str:
        """Overview of knowledge graph linking methodologies and when to use each approach"""
        return """# Knowledge Graph Linking Best Practices

This directory contains proven methodologies for connecting entities in AGS (AnzoGraph Services) knowledge graphs using SPARQL transformations.

## 📁 Documentation Structure

### Core Methodologies
- **internal_linking_guide** - Connect entities within a single domain ontology
- **cross_domain_linking_guide** - Connect entities across multiple domain ontologies

### Supporting Guides
- **sparql_query_guide** - SPARQL syntax and best practices
- **graphmart_workflow** - Step-by-step graphmart operations
- **layer_management** - Layer operations guide
- **dataset_operations** - Data upload workflows
- **ags_query_lens_guide** - Interactive visualization best practices
- **troubleshooting_guide** - Common issues and solutions

## 🎯 When to Use Each Guide

### Internal Linking
**Use when:** You have a single domain with "islands" - entities that reference each other via string foreign keys but lack object property relationships.

**Examples:**
- CRM: Opportunities reference Customers via `customerId` string
- ERP: Invoices reference Cost Centers via `costCenter` string  
- PLM: Parts reference BOMs via `bomId` string

**Result:** Navigate relationships using object properties instead of string matching.

### Cross-Domain Linking  
**Use when:** You have multiple well-linked domains that need connections between them using shared identifiers.

**Examples:**
- PLM Parts and Manufacturing Orders both have `productId`
- CRM Customer Equipment and Service Work Orders both have `equipmentId`
- Quality Issues and Supply Chain Components both have `componentId`

**Result:** Enable cross-domain queries spanning multiple business domains.

## 🏗️ Architectural Patterns

### Single Domain Architecture (Internal Linking)
```
Source Data → Domain Data Layer → Domain Internal Linking Layer
```
- **One linking ontology per domain** (e.g., `CRMLinking`, `ERPLinking`)
- **One transformation layer per domain** (e.g., "CRM Internal Linking")
- **Result:** Well-connected domain with rich object property navigation

### Multi-Domain Architecture (Cross-Domain Linking)
```
Domain 1 Internal Linking ──┐
Domain 2 Internal Linking ──┤
Domain 3 Internal Linking ──┼─→ Cross-Domain Linking (Unified)
Domain 4 Internal Linking ──┤
Domain N Internal Linking ──┘
```
- **One unified cross-domain ontology** (`CrossDomainLinking`)
- **One unified transformation layer** ("Cross-Domain Linking")  
- **Result:** Fully connected knowledge graph enabling cross-domain analytics

## ⚡ Quick Start Checklist

### For Internal Linking (Single Domain)
- [ ] Identify string foreign keys within domain
- [ ] Create `{Domain}Linking` ontology  
- [ ] Import source domain ontology
- [ ] Add object properties for each FK relationship
- [ ] Create transformation layer with INSERT steps
- [ ] Validate with SELECT queries first
- [ ] Register ontology with graphmart
- [ ] Refresh (never reload unless requested)

### For Cross-Domain Linking (Multiple Domains)  
- [ ] Complete internal linking for all domains first
- [ ] Identify shared identifiers across domains (e.g., `productId`)
- [ ] Design minimum spanning tree for connectivity
- [ ] Create unified `CrossDomainLinking` ontology (one-time)
- [ ] Import all domain ontologies (one-time)
- [ ] Add cross-domain properties for each relationship
- [ ] Create unified transformation layer (one-time)
- [ ] Test coverage and validate with SELECT queries
- [ ] Execute transformations and validate connectivity

## 🚨 Critical Success Rules

### Universal Rules (Both Internal and Cross-Domain)
1. **Never modify auto-generated ontologies** - they get recreated on reload
2. **Always test with SELECT before INSERT** - validate query logic first
3. **Always register ontologies** - unregistered ontologies won't work  
4. **Use `refresh_graphmart` by default** - only use `reload_graphmart` if explicitly requested
5. **Validate link counts** - watch for cartesian products or insufficient matches
6. **Import dependencies** - linking ontologies must import source ontologies

### Internal Linking Specific Rules
7. **One ontology per domain** - separate linking concerns by business domain
8. **One layer per domain** - pair each linking ontology with its own transformation layer
9. **Expect 70-95% coverage** - string foreign keys usually have high match rates

### Cross-Domain Specific Rules  
10. **One unified ontology for all cross-domain links** - don't create multiple cross-domain ontologies
11. **One unified layer for all cross-domain transformations** - don't create multiple cross-domain layers
12. **Accept 20-60% coverage** - cross-domain matches have lower coverage (expected)
13. **Design minimum spanning tree** - use (N-1) links to connect N domains efficiently

## 📊 Success Metrics

### Internal Linking Success
- ✅ 70%+ entity coverage within domain
- ✅ Object property navigation replaces string matching
- ✅ Domain-specific business queries enabled
- ✅ Fast query performance (<2 seconds)

### Cross-Domain Linking Success  
- ✅ All domains reachable from any other domain
- ✅ 40%+ cross-domain coverage (excellent for Phase 1)
- ✅ Cross-domain business queries enabled
- ✅ No orphaned domain islands
- ✅ Minimum number of cross-domain links used

## 🔧 Tools & Commands Reference

### Core AGS MCP Commands
```bash
# Ontology Management
mcp_ags-sparql-ag_create_ontology
mcp_ags-sparql-ag_register_ontology  
mcp_ags-sparql-ag_add_ontology_import
mcp_ags-sparql-ag_add_ontology_property

# Layer Management  
mcp_ags-sparql-ag_create_transformation_layer
mcp_ags-sparql-ag_add_transformation_step

# Execution & Validation
mcp_ags-sparql-ag_refresh_graphmart
mcp_ags-sparql-ag_execute_sparql_query
mcp_ags-sparql-ag_get_layer_status

# Discovery & Analysis
mcp_ags-sparql-ag_list_transformation_layers
mcp_ags-sparql-ag_discover_available_ontologies
mcp_ags-sparql-ag_list_ontology_structure_classes
```

### SPARQL Query Templates
Available in each methodology guide:
- Entity counting queries
- Coverage analysis queries  
- Link validation queries
- Business validation queries
- Cross-domain navigation queries

## 🎓 Learning Path

1. **Start with Internal Linking** - Master single-domain linking first
2. **Complete all domains** - Ensure each domain is well-linked internally  
3. **Move to Cross-Domain** - Connect domains using minimum spanning tree approach
4. **Iterate and expand** - Add more cross-domain relationships based on business needs

## 💡 Tips for Success

- **Start small** - Begin with highest-coverage, most obvious relationships
- **Test frequently** - Validate every step with SELECT queries
- **Document gaps** - Real-world data has quality issues (expected and acceptable)
- **Think business value** - Focus on relationships that enable important questions
- **Be patient** - Knowledge graph linking is iterative - perfection comes with time

---

*These methodologies have been proven on large-scale enterprise knowledge graphs with millions of entities and hundreds of thousands of successful links.*
"""
    
    @mcp.prompt()
    def ontology_data_layer_best_practices() -> str:
        """Best practices for creating robust ontologies and transformation layers from auto-ingested data"""
        return """# AGS Ontology & Data Layer Best Practices Guide
*A concise workflow for creating robust knowledge graphs from auto-ingested data sources*

## 🎯 Overview
This guide provides proven techniques for building ontologies and transformation layers in AGS (Anzo Graphmart Server) based on automatically ingested data sources (JSON, databases, Snowflake, etc.). Follow this workflow to rapidly create cross-domain linking ontologies with validated relationships.

---

## 🔄 Core Workflow

### Phase 1: Data Discovery & Analysis
**Goal**: Understand your data structure before creating ontologies

#### 1.1 Explore Available Data
```sparql
# Discover entity types and counts
SELECT ?type (COUNT(*) as ?count)
WHERE {
    ?entity a ?type .
    FILTER(STRSTARTS(STR(?type), "http://your-domain/ontologies/"))
}
GROUP BY ?type ORDER BY DESC(?count)
```

#### 1.2 Analyze Entity Properties
```sparql
# Find all properties for a specific class
SELECT DISTINCT ?property
WHERE {
    ?entity a domain:YourClass .
    ?entity ?property ?value .
    FILTER(STRSTARTS(STR(?property), "http://your-domain/ontologies/"))
}
ORDER BY ?property
```

#### 1.3 Sample Data Patterns
```sparql
# Examine actual data values to understand linking opportunities
SELECT ?entity ?property ?value
WHERE {
    ?entity a domain:YourClass .
    ?entity ?property ?value .
}
LIMIT 10
```

---

### Phase 2: Validate Potential Relationships
**Goal**: Test relationship feasibility before creating properties

#### 2.1 Test Cross-Domain Links with SELECT Queries
```sparql
# ALWAYS test linking logic first with SELECT
PREFIX domain1: <http://your-domain/ontologies/Domain1#>
PREFIX domain2: <http://your-domain/ontologies/Domain2#>

SELECT ?entity1 ?linkingValue ?entity2
WHERE {
    ?entity1 a domain1:SourceClass ;
        domain1:linkingProperty ?linkingValue .
    
    ?entity2 a domain2:TargetClass ;
        domain2:matchingProperty ?linkingValue .
}
LIMIT 10
```

**✅ Key Rule**: If your SELECT query returns 0 results, fix the linking logic before creating properties.

#### 2.2 Validate Domain/Range Classes
```sparql
# Verify classes exist in ontologies before using as domain/range
SELECT (COUNT(*) as ?instanceCount)
WHERE {
    ?entity a targetOntology:YourTargetClass .
}
```

---

### Phase 3: Create Minimal Linking Ontologies
**Goal**: Start small with focused, cross-domain linking ontologies

#### 3.1 Create Linking Ontology
```bash
# Use descriptive names like: DomainADomainB + "Linking"
mcp_ags-sparql-ag_create_ontology
- ontology_uri: "http://your-domain/ontologies/ERPLinking"
- ontology_label: "ERP Cross-Domain Linking"
- description: "Links ERP entities to other domain entities"
```

#### 3.2 **CRITICAL**: Register the Ontology
```bash
# ALWAYS register after creation - frequently forgotten step!
mcp_ags-sparql-ag_register_ontology
- ontology_uri: "http://your-domain/ontologies/ERPLinking"
- explanation: "Register ontology for discoverability"
```

#### 3.3 Add Object Properties Only
**Best Practice**: Start with object properties linking existing classes
```bash
mcp_ags-sparql-ag_add_ontology_property
- ontology_uri: "http://your-domain/ontologies/ERPLinking"
- property_uri: "http://your-domain/ontologies/ERPLinking#linksDomainAToB"
- property_type: "object"
- domain_uri: "http://your-domain/ontologies/DomainA#SourceClass"
- range_uri: "http://your-domain/ontologies/DomainB#TargetClass"
```

**⚠️ Avoid**: Creating new classes in linking ontologies - use existing ones

---

### Phase 4: Create Transformation Layers
**Goal**: Implement the validated relationships as transformation steps

#### 4.1 Create Transformation Layer
```bash
mcp_ags-sparql-ag_create_transformation_layer
- layer_name: "Domain Linking"
- layer_description: "Cross-domain relationship linking"
- order_after: "Domain Data"  # Put after data loading layers
```

#### 4.2 Add Transformation Steps
**Critical Pattern**: Use exact AGS template syntax
```sparql
PREFIX domain1: <http://your-domain/ontologies/Domain1#>
PREFIX domain2: <http://your-domain/ontologies/Domain2#>
PREFIX linking: <http://your-domain/ontologies/ERPLinking#>

INSERT {
    GRAPH ${targetGraph} {
        ?source linking:yourProperty ?target .
    }
}
${usingSources}
WHERE {
    # Use the exact WHERE clause from your validated SELECT query
    ?source a domain1:SourceClass ;
        domain1:linkingProperty ?linkingValue .
    
    ?target a domain2:TargetClass ;
        domain2:matchingProperty ?linkingValue .
}
```

**✅ Template Requirements**:
- `${targetGraph}` (single $, not $$)
- `${usingSources}` (single $, not $$)
- Use `\\n` for line breaks (not `\\\\n`)

---

### Phase 5: Test & Iterate
**Goal**: Validate transformation results and expand incrementally

#### 5.1 Test Transformation Results
```sparql
# After layer execution, verify new relationships exist
SELECT (COUNT(*) as ?newLinks)
WHERE {
    ?source linking:yourProperty ?target .
}
```

#### 5.2 Incremental Expansion
- **Start**: 1-2 properties per linking ontology
- **Test**: Each property individually 
- **Expand**: Add more properties once working
- **Scale**: Multiple transformation steps per layer

---

## 🛠️ Advanced Patterns

### Multi-Hop Relationships
Build chains of relationships across domains:
```
Customer --[hasSalesOrder]--> SalesOrder 
    --[becomesInstalledEquipment]--> InstalledEquipment 
        --[implementsPLMSystem]--> PLM System
```

### Hierarchical BOM Linking
For complex product structures:
```sparql
# Level → Direct Components
?level plml:hasDirectComponent ?part .

# Level → Child Assemblies  
?parentLevel plml:hasChildAssembly ?childLevel .

# Inverse: Component → Parent Assembly
?part plml:isComponentOfAssembly ?level .
```

### Bridge Orphaned Classes
Connect isolated classes to main hierarchy:
```sparql
# Link alternative representations to primary structure
?subassembly plml:correspondsToBOMLevel ?bomLevel .
?subassembly plml:containsPart ?part .
```

---

## 🚨 Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| **0 results from linking queries** | Fix SELECT query logic before creating properties |
| **"Class not found" errors** | Verify domain/range classes exist with COUNT queries |
| **Orphaned ontologies** | Always register ontologies after creation |
| **Template syntax errors** | Use single `$`, `\\n` line breaks, exact AGS format |
| **Complex queries fail** | Break into smaller, simpler transformation steps |
| **Mixed up domains/ranges** | Double-check which direction the relationship flows |

---

## 📊 Success Metrics

**Validation Checkpoints**:
- ✅ SELECT queries return expected results
- ✅ Domain/range classes have >0 instances  
- ✅ Properties appear in ontology structure lists
- ✅ Transformation steps execute without errors
- ✅ New relationships appear in result queries
- ✅ No orphaned classes in ontology viewer

**Performance Indicators**:
- **Rapid prototyping**: Validate relationships in minutes
- **Reliable execution**: Transformation steps run consistently  
- **Cross-domain navigation**: Multi-hop queries return results
- **Business value**: Enable impact analysis and traceability

---

## 🎯 Quick Reference Commands

```bash
# Discovery
mcp_ags-sparql-ag_list_available_ontologies
mcp_ags-sparql-ag_execute_sparql_query

# Creation
mcp_ags-sparql-ag_create_ontology
mcp_ags-sparql-ag_register_ontology  # DON'T FORGET!
mcp_ags-sparql-ag_add_ontology_property

# Layers
mcp_ags-sparql-ag_create_transformation_layer
mcp_ags-sparql-ag_add_transformation_step

# Validation  
mcp_ags-sparql-ag_list_transformation_steps
mcp_ags-sparql-ag_list_ontology_structure_properties
```

**Remember**: Always test with SELECT before implementing with INSERT! 🎯
"""
    
    @mcp.prompt()
    def sparql_query_guide(graphmart_name: str = "default") -> str:
        """Guide for writing effective SPARQL queries against Anzo graphmarts.
        
        Args:
            graphmart_name: Name of the graphmart to query (for context)
        """
        return f"""# SPARQL Query Best Practices for Anzo

## Query Structure
Always use proper SPARQL syntax:
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?predicate ?object
WHERE {{
  ?subject ?predicate ?object .
}}
LIMIT 100
```

## Best Practices

1. **Always use LIMIT**: Prevent large result sets
   - Start with LIMIT 10 for exploration
   - Max recommended: LIMIT 1000

2. **Use FILTERs efficiently**: Place most restrictive filters first
   ```sparql
   FILTER(?date > "2024-01-01"^^xsd:date)
   FILTER(CONTAINS(?name, "example"))
   ```

3. **Leverage indexes**: Query by known URIs when possible
   ```sparql
   <http://specific/resource> ?p ?o .
   ```

4. **Check data patterns first**: Use COUNT to understand data volume
   ```sparql
   SELECT (COUNT(*) as ?count) WHERE {{ ?s ?p ?o }}
   ```

5. **Use OPTIONAL carefully**: Can slow queries significantly
   ```sparql
   ?subject ?required ?value .
   OPTIONAL {{ ?subject ?optional ?optValue }}
   ```

## Common Patterns

### Find all types:
```sparql
SELECT DISTINCT ?type (COUNT(?s) as ?count)
WHERE {{ ?s rdf:type ?type }}
GROUP BY ?type
ORDER BY DESC(?count)
LIMIT 20
```

### Explore relationships:
```sparql
SELECT ?property (COUNT(?s) as ?usage)
WHERE {{ ?s ?property ?o }}
GROUP BY ?property
ORDER BY DESC(?usage)
LIMIT 50
```

### Search by label:
```sparql
SELECT ?resource ?label
WHERE {{
  ?resource rdfs:label ?label .
  FILTER(CONTAINS(LCASE(?label), "search term"))
}}
LIMIT 20
```

## Current Context
Graphmart: {graphmart_name}
Use execute_sparql_query tool with these patterns.
"""

    @mcp.prompt()
    def graphmart_workflow() -> str:
        """Complete workflow for managing graphmarts."""
        return """# Graphmart Management Workflow

## 1. List Available Graphmarts
Start by seeing what graphmarts exist:
- Tool: `list_graphmarts`
- Tip: Use expand="*" for full details

## 2. Check Graphmart Status
Before operations, check if graphmart is online:
- Tool: `retrieve_graphmart_status`
- Status values: online, offline, activating, error

## 3. Activate if Needed
If offline, activate before querying:
- Tool: `activate_graphmart`
- Wait time: Can take 30-60 seconds for large graphmarts

## 4. Query Data
Once online, run SPARQL queries:
- Tool: `execute_sparql_query`
- Always specify graphmart_uri or set ANZO_GRAPHMART_IRI

## 5. Check Layers
View graphmart structure:
- Tool: `retrieve_graphmart_layers`
- Shows data sources and their order

## Common Operations

### Create New Graphmart:
```json
{
  "title": "My Graphmart",
  "description": "Purpose of this graphmart",
  "acls": []
}
```

### Refresh After Data Changes:
- `refresh_graphmart` - Quick, only changed layers
- `reload_graphmart` - Full reload, all layers

### Deactivate When Done:
- `deactivate_graphmart` - Free resources

## Error Handling

- **404 Not Found**: Graphmart doesn't exist or no permission
- **409 Conflict**: Graphmart already activating
- **503 Service Unavailable**: Anzo server busy

Always check status before operations!
"""

    @mcp.prompt()
    def layer_management() -> str:
        """Guide for managing graphmart layers."""
        return """# Layer Management Guide

## What are Layers?
Layers are data sources in a graphmart. Think of them as:
- Individual datasets
- External data connections
- Virtual views

## Layer Operations

### 1. List Layers
Tool: `retrieve_graphmart_layers`
- Shows: layer URIs, names, types, status

### 2. Add Layer
Tool: `create_graphmart_layer`
Required fields:
```json
{
  "uri": "http://example.com/layer/my-layer",
  "label": "My Data Layer",
  "type": "namedGraph"
}
```

### 3. Remove Layer
Tool: `delete_graphmart_layer`
- Requires: graphmart_uri and layer_uri
- Warning: Deletes all data in that layer!

### 4. Reorder Layers
Tool: `move_graphmart_layer`
- Layers stack: last layer on top
- Use `after` or `before` parameter

## Best Practices

1. **Name layers clearly**: Use descriptive labels
2. **Order matters**: Place most used data on top
3. **Test before production**: Use test graphmart first
4. **Backup important layers**: Export data before deletion

## Common Layer Types

- **namedGraph**: Standard RDF graph
- **view**: Virtual data from query
- **external**: Remote data source
- **inference**: Reasoning results

Always check layer status after operations!
"""

    @mcp.prompt()
    def dataset_operations() -> str:
        """Guide for dataset and data import operations."""
        return """# Dataset Operations Guide

## Upload Data to Anzo

### 1. Create Empty Dataset
Tool: `create_empty_dataset`
```json
{
  "uri": "http://example.com/dataset/my-data",
  "label": "My Dataset"
}
```

### 2. Upload Data File
Tool: `upload_dataset_file`
Supported formats:
- RDF/XML (.rdf, .xml)
- Turtle (.ttl)
- N-Triples (.nt)
- JSON-LD (.jsonld)

Example:
```python
upload_dataset_file(
    dataset_uri="http://example.com/dataset/my-data",
    file_path="/path/to/data.ttl",
    format="text/turtle"
)
```

### 3. Set Dataset ACLs
Tool: `set_dataset_acl`
Control who can read/write:
```json
{
  "read": ["ldap://cn=users,dc=example"],
  "write": ["ldap://cn=admins,dc=example"]
}
```

## Best Practices

1. **Validate before upload**: Check RDF syntax locally
2. **Use appropriate format**: Turtle is most readable
3. **Batch large datasets**: Split files > 100MB
4. **Set ACLs immediately**: Don't leave data unprotected
5. **Test with small samples**: Verify structure first

## Common Errors

- **400 Bad Request**: Invalid RDF syntax
- **413 Payload Too Large**: File too big, split it
- **403 Forbidden**: Check ACLs and permissions

Always verify data loaded correctly with a SPARQL query!
"""

    @mcp.prompt()
    def ags_query_lens_guide() -> str:
        """Best practices for creating AGS Query Lens visualizations with interactive navigation"""
        return """# AGS Query Lens Visualization Best Practices

## Overview

This guide covers best practices for creating interactive, navigable visualizations using AGS Query Lenses. These patterns enable building sophisticated data exploration interfaces without complex JavaScript frameworks.

## Core Concepts

### Query Lens Structure

AGS Query Lenses consist of three main components:

1. **SPARQL Query** - Retrieves data from the knowledge graph
2. **HTML Template (EJS)** - Renders the visualization
3. **CSS Styles** - Provides visual styling

Additionally, **state variables** enable interactivity and navigation.

## State Management

### Defining State Variables

State variables enable interactive navigation and filtering:

```json
{
  "state": [
    {
      "name": "rootItem",
      "value": "DEFAULT_VALUE",
      "type": "string"
    },
    {
      "name": "path",
      "value": "DEFAULT_VALUE",
      "type": "string"
    }
  ]
}
```

### Accessing State in Queries

Use EJS template syntax to inject state into SPARQL:

```sparql
<% 
  const rootItem = state['rootItem'] || 'DEFAULT_VALUE';
%>

SELECT ?child ?childName ?childType
WHERE {
  ?parent :itemId '<%= rootItem %>' .
  ?child :parentRef ?parent ;
         :itemId ?childId .
  OPTIONAL { ?child :name ?childName }
  OPTIONAL { ?child :type ?childType }
}
```

## Interactive Navigation Pattern

### The Hidden Input + onclick Pattern

AGS automatically binds form elements with `name` attributes to state variables. The recommended pattern:

1. **Add hidden inputs** for each state variable
2. **Use onclick handlers** to update values and trigger refresh
3. **Dispatch change events** to notify AGS of state updates

### Implementation

```html
<!-- Hidden inputs bound to state -->
<input type="hidden" name="rootItem" value="<%=rootItem%>" />
<input type="hidden" name="path" value="<%=pathStr%>" />

<!-- Navigation button -->
<button onclick="var el=document.querySelector('[name=rootItem]');el.value='NEW_VALUE';el.dispatchEvent(new Event('change',{bubbles:true}))">
  Navigate
</button>
```

### Key Points

- Form elements with `name` attribute auto-bind to state
- Use `dispatchEvent(new Event('change', {bubbles:true}))` to trigger lens refresh
- AGS handles the refresh automatically - no need to call `lens.refresh()` explicitly

## Breadcrumb Navigation

### Path Tracking Strategy

Use a delimited string to track navigation history:

```javascript
// Store path as: "LEVEL1>LEVEL2>LEVEL3"
const pathStr = state['path'] || 'ROOT_VALUE';
const pathItems = pathStr.split('>');
```

### Navigation Helper Function

```javascript
function makeNavCode(itemId, pathStr) {
  const items = pathStr.split('>');
  const idx = items.indexOf(itemId);
  let newPath;
  
  // Backward navigation (item already in path)
  if (idx >= 0) {
    newPath = items.slice(0, idx + 1).join('>');
  } 
  // Forward navigation (new item)
  else {
    newPath = pathStr + '>' + itemId;
  }
  
  return "var e1=document.querySelector('[name=rootItem]');e1.value='" + itemId + 
         "';var e2=document.querySelector('[name=path]');e2.value='" + newPath + 
         "';e1.dispatchEvent(new Event('change',{bubbles:true}))";
}
```

### Rendering Breadcrumbs

```html
<div class="breadcrumb">
  <% pathItems.forEach((item, idx) => { %>
    <% if (idx > 0) { %><span class="separator">›</span><% } %>
    <% const isActive = idx === pathItems.length - 1; %>
    <span class="breadcrumb-item <%= isActive ? 'active' : '' %>" 
          <% if (!isActive) { %>
            onclick="<%=makeNavCode(item, pathStr)%>" 
            style="cursor:pointer"
          <% } %>>
      <% if (idx === 0) { %>🏠 <% } %><%=item%>
    </span>
  <% }); %>
</div>
```

## SPARQL Query Best Practices

### Keep Queries Simple

- **Avoid nested SELECT subqueries** - AGS query lenses work best with flat queries
- **Use OPTIONAL for nullable fields** - Prevents query from failing on missing data
- **Limit result sets** - Use `LIMIT` to prevent performance issues

### Pattern: Hierarchical Navigation Query

```sparql
PREFIX ex: <http://example.com/ontology#>

<% const currentNode = state['currentNode'] || 'ROOT'; %>

SELECT ?childNode ?childId ?childName ?childType ?quantity
WHERE {
  # Find the current node
  ?parent ex:nodeId '<%= currentNode %>' .
  
  # Find direct children
  ?childNode ex:parentNode ?parent ;
             ex:nodeId ?childId .
  
  # Get optional properties
  OPTIONAL { ?childNode ex:name ?childName }
  OPTIONAL { ?childNode ex:type ?childType }
  OPTIONAL { ?childNode ex:quantity ?quantity }
}
ORDER BY ?childName
LIMIT 100
```

## Data Processing in EJS

### Building Data Structures

```javascript
<%
  const items = [];
  const currentNode = state['currentNode'] || 'ROOT';
  
  bindings.forEach(b => {
    if (b.childId) {
      items.push({
        id: b.childId?.value,
        name: b.childName?.value || 'Unnamed',
        type: b.childType?.value || 'Unknown',
        quantity: b.quantity?.value || '1'
      });
    }
  });
%>
```

### Helper Functions for Display

```javascript
function getIcon(type) {
  if (type.includes('Category1')) return '🔵';
  if (type.includes('Category2')) return '🟢';
  return '⚪';
}

function getColor(type) {
  if (type.includes('Category1')) return '#1976D2';
  if (type.includes('Category2')) return '#00897B';
  return '#616161';
}
```

## CSS Styling Recommendations

### Modern Gradient Headers

```css
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px 32px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}
```

### Interactive Breadcrumbs

```css
.breadcrumb-item {
  color: #667eea;
  transition: all 0.2s;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 500;
}

.breadcrumb-item:not(.active):hover {
  background: #f0f4ff;
  color: #5568d3;
  transform: translateY(-1px);
}

.breadcrumb-item.active {
  color: #2c3e50;
  background: #e6f2ff;
  font-weight: 600;
  cursor: default;
}
```

### Animated Table Rows

```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.table-row {
  animation: slideIn 0.3s ease-out backwards;
}

.table-row:nth-child(1) { animation-delay: 0.05s; }
.table-row:nth-child(2) { animation-delay: 0.1s; }
.table-row:nth-child(3) { animation-delay: 0.15s; }
```

## Common Patterns

### Summary Cards

Display key metrics at a glance:

```html
<div class="summary-grid">
  <div class="card">
    <div class="card-icon">📦</div>
    <div class="card-content">
      <div class="card-value"><%=items.length%></div>
      <div class="card-label">Total Items</div>
    </div>
  </div>
  <div class="card">
    <div class="card-icon">📊</div>
    <div class="card-content">
      <div class="card-value"><%=pathItems.length%></div>
      <div class="card-label">Current Level</div>
    </div>
  </div>
</div>
```

### Empty State Messaging

```html
<% if (items.length === 0) { %>
  <div class="empty-state">
    <div class="empty-icon">📭</div>
    <h3>No Data Found</h3>
    <p>Try adjusting your filters or navigating to a different node.</p>
  </div>
<% } %>
```

### Export Functionality

AGS provides built-in export capability:

```html
<button class="btn exportButton" filename="data_export" format="csv">
  📥 Export CSV
</button>
```

## Troubleshooting

### Navigation Not Working

**Problem:** Clicking navigation buttons does nothing

**Solution:** Ensure you're:
1. Using hidden inputs with `name` attributes
2. Dispatching `change` events with `bubbles:true`
3. Updating the correct input element

### Query Syntax Errors

**Problem:** SPARQL query fails with nested SELECT errors

**Solution:**
- Remove nested `SELECT` subqueries
- Use flat query structure with `OPTIONAL` clauses
- Avoid `WITH` clauses in the main query body

### State Not Persisting

**Problem:** State resets after navigation

**Solution:**
- Verify hidden inputs have `name` attributes matching state variable names
- Ensure `value` attribute is set to current state: `value="<%=stateVar%>"`
- Check that navigation code updates both state variables

## Performance Considerations

1. **Limit Query Results:** Use `LIMIT` to cap result sets
2. **Index Properties:** Ensure frequently queried properties are indexed in AGS
3. **Minimize Data Processing:** Do complex calculations in SPARQL when possible
4. **Cache Static Data:** Use EJS variables for data that doesn't change per row

## Summary

The key to successful AGS Query Lens visualizations:

1. ✅ Use state variables for navigation and filtering
2. ✅ Bind state via hidden form inputs with `name` attributes
3. ✅ Update state with `dispatchEvent(new Event('change', {bubbles:true}))`
4. ✅ Keep SPARQL queries flat and simple
5. ✅ Implement breadcrumb navigation for multi-level exploration
6. ✅ Provide visual feedback with modern CSS and animations
7. ✅ Handle empty states gracefully

This pattern enables building sophisticated, interactive data exploration tools entirely within AGS Query Lenses, without requiring external web frameworks or complex JavaScript.
"""

    @mcp.prompt()
    def cross_domain_linking_guide() -> str:
        """Best practices for connecting domain ontologies using minimum spanning tree approach"""
        return """# Cross-Domain Linking Best Practices
**A Step-by-Step Guide for Connecting Domain Islands with Minimum Spanning Tree Approach**

## 🎯 Purpose

This guide provides a proven workflow for connecting multiple domain ontologies that have been internally linked but remain isolated "islands" in a knowledge graph. It creates cross-domain object property relationships using shared identifiers.

**When to Use**: When you have multiple well-linked domain ontologies (e.g., CRM, ERP, PLM, Manufacturing) but they lack connections between domains.

**Example**: PLM Parts have `productId` and MES Production Orders have `productId`, but no direct object property links exist between them.

---

## ✅ The Golden Rules (Adapted from Internal Linking)

### Rule #1: Foreign Keys and Shared Attributes First
**Internal Linking:** Look for explicit FKs within domain (e.g., `Order.customerId` → `Customer.id`)  
**Cross-Domain Adaptation:** Look for **shared identifiers across domains**:
- `productId` (may appear in PLM, Manufacturing, Quality, Regulatory, Service)
- `customerId` (may appear in CRM, Service, Finance)
- `equipmentId` (may appear in CRM, Service, Manufacturing)
- `supplierId` (may appear in Supply Chain, Quality, Finance)
- `batchNumber`/`lotNumber` (may appear in Manufacturing, Supply Chain, Quality)

**Action:** Catalog all shared identifiers and their coverage percentages across domain pairs.

### Rule #2: Validate with SELECT COUNT Before Creating Links
**Same as Internal:** Always test link queries with `SELECT (COUNT(*) as ?links)` before implementing.

**Cross-Domain Caution:** 
- Coverage may be lower than internal links (expect 20-60% vs 70-95%)
- Identifier naming may vary (e.g., `productId` vs `productNumber` vs `partNumber`)
- Data quality gaps more common across domain boundaries

**Action:** Accept lower coverage for Phase 1 if connection is semantically valid.

### Rule #3: Avoid Cartesian Products
**Same as Internal:** Validate that link counts << (sourceCount × targetCount)

**Cross-Domain Example:**
```sparql
# GOOD: Specific FK match
SELECT (COUNT(*) as ?links) WHERE {
    ?sourceEntity source:Class.idProperty ?sharedId .
    ?targetEntity target:Class.idProperty ?sharedId .
}
# Result: Should be much less than (sourceCount × targetCount)
```

### Rule #4: Single Unified Cross-Domain Architecture
**Internal Linking:** One ontology per domain (e.g., `{UUID}/PLMLinking`, `{UUID}/CRMLinking`) + One layer per domain  
**Cross-Domain Adaptation:** **ONE unified ontology + ONE unified layer** for all cross-domain relationships

**Naming Convention:**
- **Ontology URI:** `{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking`
- **Layer Name:** "Cross-Domain Linking"
- **Properties:** Descriptive names indicating source and target domains
  - `relatedProductionOrder` (PLM → Manufacturing)
  - `relatedQualityIssue` (PLM → Quality)
  - `relatedCustomerFeedback` (Service → CRM)

**UUID Generation**: Use an 8-character hex UUID to ensure global uniqueness across graphmarts:
```python
import uuid
short_uuid = uuid.uuid4().hex[:8]
# Use in URI: f"{YOUR_BASE_URI}/ontologies/{short_uuid}/CrossDomainLinking"
```

**Rationale:**
- **Architectural Consistency:** Single ontology pairs with single layer
- **Simplicity:** One ontology + one layer to register, maintain, and version
- **Discoverability:** All cross-domain relationships in one place
- **Flexibility:** Easy to add new cross-domain properties without creating new ontologies
- **Operational Efficiency:** Single layer refresh for all cross-domain links

### Rule #5: Refresh Only, Never Reload
**Same as Internal:** Use `refresh_graphmart` exclusively, avoid `reload_graphmart`.

### Rule #6: Register Every Ontology
**Same as Internal:** ALWAYS register ontologies immediately after creation!

### Rule #7: Import All Domain Ontologies
**Cross-Domain Adaptation:** The unified CrossDomainLinking ontology imports **ALL domain ontologies**.

**Benefit:** Single import statement covers all cross-domain property domain/range references.

### Rule #8: Validate Coverage Percentages
**Internal Linking:** Expected 70-95% coverage for direct FKs  
**Cross-Domain Adjustment:** Accept 20-60% coverage for Phase 1 connectivity

**Coverage Tiers:**
- **Excellent (60%+):** Strong cross-domain relationship, consider additional properties
- **Good (40-60%):** Solid Phase 1 connection
- **Acceptable (20-40%):** Sufficient for minimum connectivity
- **Weak (<20%):** Consider alternative linking strategy

---

## Cross-Domain Linking Strategy: Minimum Spanning Tree

### Graph Theory Approach
**Objective:** Connect N domains with minimum edges (cross-domain links)  
**Minimum:** (N-1) cross-domain links required for full connectivity  
**Strategy:** Prioritize high-coverage, semantically rich connections

### Phase 1: Minimum Viable Connectivity
**Goal:** Create minimum spanning tree where every domain is reachable from every other domain via graph traversal.

**Success Criteria:**
- ✅ All domains reachable from any other domain via graph traversal
- ✅ No orphaned domain islands
- ✅ Minimum number of cross-domain links ((N-1) links for N domains)
- ✅ High data quality connections (>40% coverage preferred)

### Phase 2: Business-Driven Expansion
**Goal:** Add additional cross-domain relationships based on specific business questions and use cases.

---

## Methodology: 8-Step Process

### Step 1: Domain Discovery & Analysis
**Identify your domains and their key entities:**

1.1. **List Available Domains**
```bash
mcp_ags-sparql-ag_list_transformation_layers
# Look for internal linking layers to identify domains
# Example output: "PLM Internal Linking", "CRM Internal Linking", etc.
```

1.2. **Catalog Domain Entities**
For each domain, find the main entity types:
```sparql
PREFIX domain: <{DOMAIN_ONTOLOGY_URI}#>

SELECT ?type (COUNT(DISTINCT ?entity) as ?count)
WHERE {
    ?entity a ?type .
    FILTER(STRSTARTS(STR(?type), "{DOMAIN_ONTOLOGY_URI}#"))
}
GROUP BY ?type
ORDER BY DESC(?count)
```

1.3. **Identify Shared Identifier Patterns**
Look for properties that might match across domains:
```sparql
PREFIX domain: <{DOMAIN_ONTOLOGY_URI}#>

# Find all datatype properties (potential foreign keys)
SELECT DISTINCT ?property (COUNT(?entity) as ?usage)
WHERE {
    ?entity ?property ?value .
    FILTER(isLiteral(?value))
    FILTER(STRSTARTS(STR(?property), "{DOMAIN_ONTOLOGY_URI}#"))
}
GROUP BY ?property
ORDER BY DESC(?usage)
```

### Step 2: Cross-Domain Coverage Analysis
**For each potential domain pair:**

2.1. **Test Shared Identifier Overlap**
```sparql
PREFIX domain1: <{DOMAIN1_ONTOLOGY_URI}#>
PREFIX domain2: <{DOMAIN2_ONTOLOGY_URI}#>

# Example: Test productId overlap between PLM and Manufacturing
SELECT 
    (COUNT(DISTINCT ?domain1Entity) as ?domain1Count)
    (COUNT(DISTINCT ?domain2Entity) as ?domain2Count)
    (COUNT(DISTINCT ?sharedId) as ?sharedIdCount)
    (COUNT(*) as ?totalPotentialLinks)
WHERE {
    ?domain1Entity domain1:EntityClass.idProperty ?sharedId .
    ?domain2Entity domain2:EntityClass.idProperty ?sharedId .
}
```

2.2. **Calculate Coverage Percentages**
```sparql
# Get baseline entity counts for each domain
SELECT (COUNT(?entity) as ?totalDomain1) WHERE { ?entity a domain1:EntityClass . }
SELECT (COUNT(?entity) as ?totalDomain2) WHERE { ?entity a domain2:EntityClass . }

# Calculate coverage:
# domain1Coverage = domain1Count / totalDomain1
# domain2Coverage = domain2Count / totalDomain2
```

2.3. **Create Coverage Matrix**
Document results in a table:
| Source Domain | Target Domain | Shared Attribute | Links | Source Coverage | Target Coverage | Priority |
|---------------|---------------|------------------|-------|-----------------|-----------------|----------|
| PLM | Manufacturing | productId | 45,000 | 72% | 90% | HIGH |
| PLM | Quality | productId | 15,000 | 60% | 30% | MEDIUM |
| Service | CRM | equipmentId | 8,000 | 80% | 65% | HIGH |

### Step 3: Design Minimum Spanning Tree
**Select cross-domain links for Phase 1:**

3.1. **Prioritize High-Coverage Links**
- Start with highest coverage percentages
- Ensure semantic validity (do the IDs actually represent the same entities?)
- Aim for business-critical connections

3.2. **Ensure Full Connectivity**
- Every domain must be reachable from every other domain
- Use graph theory: need exactly (N-1) edges for N nodes
- Check that your selected links form a connected graph

3.3. **Example Spanning Tree Strategy**
For 5 domains (PLM, Manufacturing, Quality, Service, CRM):
```
PLM (Central Hub)
├── Manufacturing (productId)
├── Quality (productId)  
└── Service (productId/equipmentId)
    └── CRM (equipmentId)
```
**Result:** 4 links connect 5 domains (minimum spanning tree)

### Step 4: Create Unified Cross-Domain Architecture (ONCE)
**Execute only ONCE before creating any cross-domain links:**

4.1. **Create Single Unified Ontology**
```bash
mcp_ags-sparql-ag_create_ontology
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking"
- ontology_label: "Cross-Domain Linking"
- description: "Defines relationships connecting entities across multiple domain ontologies"
- explanation: "Creating unified ontology for all cross-domain relationships"
```

4.2. **Register Ontology** (Don't forget!)
```bash
mcp_ags-sparql-ag_register_ontology
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking"
- explanation: "Registering cross-domain ontology with graphmart"
```

4.3. **Import All Domain Ontologies**
```bash
# For each domain ontology URI identified in Step 1
mcp_ags-sparql-ag_add_ontology_import
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking"
- imported_ontology_uri: "{DOMAIN_ONTOLOGY_URI}"
- explanation: "Importing {domain} ontology for cross-domain property references"
```

4.4. **Create Single Unified Transformation Layer**
```bash
mcp_ags-sparql-ag_create_transformation_layer
- layer_name: "Cross-Domain Linking"
- layer_description: "Connects entities across domains using shared identifiers"
- order_after: "{Last Internal Linking Layer}"
- explanation: "Creating unified layer for all cross-domain transformations"
```

### Step 5: Add Cross-Domain Properties
**For each cross-domain relationship in your spanning tree:**

5.1. **Create Object Property**
```bash
mcp_ags-sparql-ag_add_ontology_property
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking"
- property_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#{propertyName}"
- property_type: "object"
- property_label: "{Human Readable Label}"
- property_description: "Links {source_domain} {source_class} to {target_domain} {target_class} via {shared_attribute}"
- domain_uri: "{SOURCE_DOMAIN_ONTOLOGY_URI}#{SourceClass}"
- range_uri: "{TARGET_DOMAIN_ONTOLOGY_URI}#{TargetClass}"
- explanation: "Adding cross-domain property: {source_domain} → {target_domain}"
```

**Property Naming Convention**:
- `related{TargetDomainEntity}` (e.g., `relatedProductionOrder`, `relatedQualityIssue`)
- Include domain context when ambiguous
- Keep names descriptive and intuitive

### Step 6: Test Cross-Domain Queries
**CRITICAL**: Test each cross-domain query as SELECT before adding transformation steps!

6.1. **Validate Cross-Domain Query**
```sparql
PREFIX source: <{SOURCE_DOMAIN_ONTOLOGY_URI}#>
PREFIX target: <{TARGET_DOMAIN_ONTOLOGY_URI}#>

# Test the WHERE clause logic
SELECT ?sourceEntity ?targetEntity ?sharedId
WHERE {
    ?sourceEntity a source:SourceClass ;
        source:SourceClass.idProperty ?sharedId .
    ?targetEntity a target:TargetClass ;
        target:TargetClass.idProperty ?sharedId .
}
LIMIT 10
```

6.2. **Count Total Potential Links**
```sparql
SELECT (COUNT(*) as ?totalLinks)
WHERE {
    ?sourceEntity a source:SourceClass ;
        source:SourceClass.idProperty ?sharedId .
    ?targetEntity a target:TargetClass ;
        target:TargetClass.idProperty ?sharedId .
}
```

**Validation Checklist**:
- [ ] Total links match expected coverage from Step 2
- [ ] No cartesian product (links << sourceCount × targetCount)
- [ ] Sample results show semantically valid matches
- [ ] Query execution time reasonable (<5 seconds)

### Step 7: Add Cross-Domain Transformation Steps
**For each validated cross-domain relationship:**

7.1. **Create Transformation Step**
```bash
mcp_ags-sparql-ag_add_transformation_step
- layer_name_or_uri: "Cross-Domain Linking"
- step_name: "Link {SourceDomain} to {TargetDomain}"
- insert_query: "{SPARQL_INSERT_QUERY}"
- explanation: "Creating {source_domain} → {target_domain} links via {shared_attribute}"
```

7.2. **Transformation Query Template**
```sparql
PREFIX source: <{SOURCE_DOMAIN_ONTOLOGY_URI}#>
PREFIX target: <{TARGET_DOMAIN_ONTOLOGY_URI}#>
PREFIX xd: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#>

INSERT {
    GRAPH ${targetGraph} {
        ?sourceEntity xd:{propertyName} ?targetEntity .
    }
}
${usingSources}
WHERE {
    # Use EXACT WHERE clause from validated SELECT query
    ?sourceEntity a source:SourceClass ;
        source:SourceClass.idProperty ?sharedId .
    ?targetEntity a target:TargetClass ;
        target:TargetClass.idProperty ?sharedId .
}
```

**Critical Template Requirements**:
- Use `${targetGraph}` (single $, not $$)
- Use `${usingSources}` (single $, not $$)
- Use `\\n` for line breaks (not `\\\\n`)
- Copy exact WHERE clause from validated SELECT query

### Step 8: Execute and Validate Cross-Domain Links

8.1. **Refresh Graphmart**
```bash
mcp_ags-sparql-ag_refresh_graphmart
- explanation: "Executing cross-domain linking transformations"
```

8.2. **Validate Link Creation**
```sparql
PREFIX xd: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#>

# Count links for each cross-domain property
SELECT ?property (COUNT(*) as ?linkCount)
WHERE {
    ?source ?property ?target .
    FILTER(STRSTARTS(STR(?property), "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#"))
}
GROUP BY ?property
```

8.3. **Test Cross-Domain Navigation**
```sparql
PREFIX source: <{SOURCE_DOMAIN_ONTOLOGY_URI}#>
PREFIX target: <{TARGET_DOMAIN_ONTOLOGY_URI}#>
PREFIX xd: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#>

# Example: Navigate from source domain to target domain
SELECT ?sourceName ?targetName
WHERE {
    ?sourceEntity a source:SourceClass ;
        source:SourceClass.nameProperty ?sourceName ;
        xd:{propertyName} ?targetEntity .
    ?targetEntity target:TargetClass.nameProperty ?targetName .
}
ORDER BY ?sourceName
LIMIT 10
```

8.4. **Test Full Graph Connectivity**
```sparql
# Example: Multi-hop query across multiple domains
PREFIX domain1: <{DOMAIN1_ONTOLOGY_URI}#>
PREFIX domain2: <{DOMAIN2_ONTOLOGY_URI}#>
PREFIX domain3: <{DOMAIN3_ONTOLOGY_URI}#>
PREFIX xd: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/CrossDomainLinking#>

SELECT ?domain1Entity ?domain2Entity ?domain3Entity
WHERE {
    ?domain1Entity a domain1:EntityClass ;
        xd:relatedDomain2Entity ?domain2Entity .
    ?domain2Entity xd:relatedDomain3Entity ?domain3Entity .
}
LIMIT 5
```

---

## 📊 Success Metrics

### Connectivity Metrics
- ✅ **All domains reachable** - Every domain can reach every other domain via traversal
- ✅ **Minimum links achieved** - Used (N-1) links for N domains (no over-linking)
- ✅ **No orphaned islands** - No domains completely isolated

### Coverage Metrics  
- ✅ **40%+ cross-domain coverage** - Excellent for Phase 1
- ✅ **20-40% cross-domain coverage** - Good for Phase 1
- ⚠️ **<20% cross-domain coverage** - Consider alternative linking strategies

### Business Value Metrics
- ✅ **Cross-domain queries enabled** - Can answer questions spanning multiple domains
- ✅ **Graph traversal possible** - Can navigate from any domain to any other domain
- ✅ **Analytics enhanced** - Can perform cross-domain aggregations and correlations

---

## 🚨 Common Pitfalls & Solutions

| Problem | Cross-Domain Specific Solution |
|---------|--------------------------------|
| **Low cross-domain coverage** | Expected! Start with best available links, improve in Phase 2 |
| **Identifier name mismatches** | Map variations (`productId` vs `partNumber`) in transformation |
| **Multiple ontologies created** | Use single unified CrossDomainLinking ontology for all links |
| **Data quality issues** | Document gaps, focus on semantic validity over perfect coverage |
| **Complex business rules** | Start simple (direct ID matching), add complexity in Phase 2 |
| **Performance degradation** | Cross-domain queries are naturally slower - optimize as needed |
| **Forgot domain imports** | Import ALL domain ontologies into the unified cross-domain ontology |

---

## 🎯 Quick Reference Template

**Replace these placeholders in all examples**:
- `{YOUR_BASE_URI}` - Your organization's base URI (e.g., `http://company.com`)
- `{SHORT_UUID}` - 8-character hex UUID for global uniqueness (e.g., `7b4d8f2a`)
- `{DOMAIN_ONTOLOGY_URI}` - Individual domain ontology URI  
- `{SOURCE_DOMAIN_ONTOLOGY_URI}` / `{TARGET_DOMAIN_ONTOLOGY_URI}` - Specific domain URIs
- `{propertyName}` - Your cross-domain property name
- `{SourceClass}` / `{TargetClass}` - Entity class names from different domains
- `{shared_attribute}` - The identifier used for matching across domains

**Generate UUID**:
```python
import uuid
short_uuid = uuid.uuid4().hex[:8]  # e.g., "7b4d8f2a"
```

**Example Cross-Domain URIs**:
- Cross-Domain Ontology: `http://company.com/ontologies/7b4d8f2a/CrossDomainLinking`  
- Property: `http://company.com/ontologies/7b4d8f2a/CrossDomainLinking#relatedProductionOrder`
- Layer: "Cross-Domain Linking"

**Architecture Pattern**:
```
Domain 1 Internal Linking ──┐
Domain 2 Internal Linking ──┤
Domain 3 Internal Linking ──┼─→ Cross-Domain Linking (Unified Layer)
Domain 4 Internal Linking ──┤
Domain 5 Internal Linking ──┘
```

This creates a clean separation between internal domain linking (multiple layers) and cross-domain linking (single unified layer).
"""

    @mcp.prompt()
    def internal_linking_guide() -> str:
        """Best practices for connecting islands within a single domain ontology using object properties"""
        return """# Internal Linking Best Practices
**A Step-by-Step Guide for Connecting Islands Within a Single Domain Ontology**

## 🎯 Purpose

This guide provides a proven workflow for fixing "islands" within auto-generated ontologies by creating object property relationships between entities that currently only have string-based foreign key references.

**When to Use**: When entities within the same domain reference each other via string properties (like `customerId`, `equipmentId`, etc.) but lack proper graph relationships.

**Example**: CRM Opportunities have a `customerId` string property but no direct object property link to Customer.Account entities.

---

## ✅ The Golden Rules

1. **Never modify auto-generated ontologies** - they get recreated on graphmart reload
2. **Always create a separate linking ontology** (e.g., `{Domain}Linking`)
3. **Import the source ontology** so you can reference its classes
4. **Test with SELECT queries first** before creating INSERT transformation steps
5. **ALWAYS use `refresh_graphmart`, NEVER use `reload_graphmart`** unless explicitly requested by user
6. **Validate SELECT result counts** to detect cartesian products or insufficient matches
7. **Register the ontology** with the graphmart
8. **Validate results** with queries to confirm linking worked

---

## 📋 Step-by-Step Process

### Step 1: Discover the Islands (Investigation Phase)

#### 1.1 Find Entity Counts
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX domain: <{YOUR_DOMAIN_ONTOLOGY_URI}#>

SELECT ?type (COUNT(DISTINCT ?entity) as ?count)
WHERE {
    ?entity a ?type .
    FILTER(STRSTARTS(STR(?type), "{YOUR_DOMAIN_ONTOLOGY_URI}#"))
}
GROUP BY ?type
ORDER BY DESC(?count)
```

**Goal**: Identify all entity types and their counts to understand the data landscape.

#### 1.2 Examine Ontology Structure
```bash
# List all classes in the ontology
mcp_ags-sparql-ag_list_ontology_structure_classes
- ontology_uri: "{SOURCE_LAYER_ONTOLOGY_URI}"

# List all properties
mcp_ags-sparql-ag_list_ontology_structure_properties
- ontology_uri: "{SOURCE_LAYER_ONTOLOGY_URI}"
```

**Goal**: Understand existing object properties vs datatype properties (foreign keys).

#### 1.3 Test for Potential Links

**IMPORTANT**: Test each potential link type separately for better performance and clearer results.

```sparql
# Example: Can we link Entity A to Entity B via shared ID?
PREFIX domain: <{YOUR_DOMAIN_ONTOLOGY_URI}#>

SELECT (COUNT(*) as ?totalLinks)
WHERE {
    ?entityA a domain:TypeA ;
        domain:TypeA.foreignKeyProperty ?sharedId .
    ?entityB a domain:TypeB ;
        domain:TypeB.idProperty ?sharedId .
}
```

**Goal**: Validate that string-based foreign keys can successfully match entities.

**Expected Results**: 
- ✅ Many matches → Good candidate for linking
- ❌ Zero matches → Check property names or data quality issues
- ⚠️ Some matches → Data quality issues may exist (acceptable, document them)

**Best Practice**: Run a separate COUNT query for each potential link type rather than combining them with UNION. This improves performance and makes results easier to interpret.

---

### Step 2: Create Linking Ontology

#### 2.1 Create the Ontology
```bash
mcp_ags-sparql-ag_create_ontology
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking"
- ontology_label: "{Domain} Internal Linking"
- description: "Links {domain} entities internally using object properties to replace string-based foreign key references"
- explanation: "Creating separate linking ontology to avoid modifying auto-generated ontology"
```

**Naming Convention**: `{SHORT_UUID}/{Domain}Linking` (e.g., `a3f9c2e1/CRMLinking`, `7b4d8f2a/ERPLinking`)

**UUID Generation**: Use an 8-character hex UUID to ensure global uniqueness across graphmarts. Simply generate a random 8-character hex string (e.g., `7f3a2c91`, `b4e8d1f6`, `9c2a5e73`). You can use any method to generate this - the key is that it should be unique enough to avoid collisions.


#### 2.2 Register the Ontology
```bash
mcp_ags-sparql-ag_register_ontology
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking"
- explanation: "Registering ontology with graphmart for discoverability"
```

**⚠️ CRITICAL**: Don't forget this step! Unregistered ontologies won't be discoverable.

#### 2.3 Add Import Statement
```bash
# First, identify the source layer ontology URI
mcp_ags-sparql-ag_list_transformation_layers
# Find the data loading layer, note its layer_uri
# The ontology URI is typically: {layer_uri}/Model

# Then add the import
mcp_ags-sparql-ag_add_ontology_import
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking"
- imported_ontology_uri: "{SOURCE_LAYER_ONTOLOGY_URI}"
- explanation: "Importing source ontology so linking properties can reference its classes"
```

**Why**: Your linking properties need to reference classes from the auto-generated ontology.

---

### Step 3: Add Linking Properties

For each identified linking opportunity, add an object property:

```bash
mcp_ags-sparql-ag_add_ontology_property
- ontology_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking"
- property_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#{propertyName}"
- property_type: "object"
- property_label: "{Human Readable Label}"
- property_description: "Links {source} to {target} via {matching_attribute}"
- domain_uri: "{SOURCE_ONTOLOGY_URI}#{SourceClass}"
- range_uri: "{SOURCE_ONTOLOGY_URI}#{TargetClass}"
- explanation: "Adding object property to link {source} to {target}"
```

**Property Naming Convention**:
- `relatedCustomer`, `relatedProduct`, `relatedEquipment` - generic relationship
- `feedbackForCustomer`, `orderForProduct` - specific relationship type
- Keep names clear and descriptive

**Template Example**:
```bash
# Property: Entity A → Entity B
property_uri: "{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#related{TargetEntity}"
domain_uri: "{SOURCE_ONTOLOGY_URI}#{SourceEntityClass}"
range_uri: "{SOURCE_ONTOLOGY_URI}#{TargetEntityClass}"
```

---

### Step 4: Create Transformation Layer

```bash
mcp_ags-sparql-ag_create_transformation_layer
- layer_name: "{Domain} Internal Linking"
- layer_description: "Links {domain} entities internally: {list key relationships}"
- order_after: "{Domain} Data Loading"
- explanation: "Creating transformation layer to execute linking logic"
```

**Naming Convention**: `{Domain} Internal Linking`

**Ordering**: Always place immediately after the corresponding data loading layer.

---

### Step 5: Test Transformation Queries

**CRITICAL**: Test each linking query as SELECT before adding as transformation step!

#### 5.1 Validate Linking Query
```sparql
PREFIX domain: <{SOURCE_ONTOLOGY_URI}#>
PREFIX linking: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#>

# Test the WHERE clause logic
SELECT ?source ?target ?matchingValue
WHERE {
    ?source a domain:SourceClass ;
        domain:SourceClass.foreignKeyProperty ?matchingValue .
    ?target a domain:TargetClass ;
        domain:TargetClass.idProperty ?matchingValue .
}
LIMIT 10
```

**Expected Results**:
- ✅ Should see multiple matches with valid entity URIs
- ❌ Zero results → Fix the WHERE clause before proceeding

#### 5.2 **CRITICAL: Count Total Potential Links**
```sparql
PREFIX domain: <{SOURCE_ONTOLOGY_URI}#>

# Count how many links would be created
SELECT (COUNT(*) as ?totalLinks)
WHERE {
    ?source a domain:SourceClass ;
        domain:SourceClass.foreignKeyProperty ?matchingValue .
    ?target a domain:TargetClass ;
        domain:TargetClass.idProperty ?matchingValue .
}
```

**Sanity Check Analysis** (REQUIRED):
- ✅ **Reasonable**: Total links ≈ number of source entities (1:1 or 1:few relationship)
  - Example: 5,000 opportunities → 3,500 links = Good (70% coverage)
  - Example: 150,000 financial transactions → 32,243 links = Good (nested object, many don't have cost centers)
  
- ⚠️ **Warning**: Total links >> number of source entities (possible many:many without proper filters)
  - Example: 5,000 opportunities → 50,000 links = Review query! Likely missing a filter
  - Check: Are you accidentally creating multiple links per entity?
  
- 🚨 **CARTESIAN PRODUCT**: Total links = (sources × targets) or close to it
  - Example: 1,000 sources, 10 targets → 10,000 links = **DANGER!** Missing FILTER/JOIN condition
  - Fix: Add proper matching condition or additional filters
  
- ❌ **Too Few**: Total links << expected based on entity counts
  - Example: 5,000 opportunities → 50 links = Data quality issue or filters too strict
  - Check: Are property names correct? Are there whitespace/normalization issues?

**Action Required**: 
- If count looks suspicious (too high or too low), **DO NOT PROCEED**
- Investigate the query logic, add filters, or adjust matching conditions
- Re-test until count makes business sense
- Document expected vs actual link counts in analysis

#### 5.3 Check for Data Quality Issues
```sparql
# Find orphaned references (source entities with no matching target)
SELECT ?source ?orphanedId
WHERE {
    ?source a domain:SourceClass ;
        domain:SourceClass.foreignKeyProperty ?orphanedId .
    FILTER NOT EXISTS {
        ?target a domain:TargetClass ;
            domain:TargetClass.idProperty ?orphanedId .
    }
}
LIMIT 100
```

**Action**: Document orphaned references - they're expected in real-world data.

#### 5.4 Calculate Expected Coverage
```sparql
# Count source entities with matching foreign keys
SELECT 
    (COUNT(DISTINCT ?source) as ?totalSources)
    (COUNT(DISTINCT ?sourceWithFK) as ?sourcesWithFK)
WHERE {
    { ?source a domain:SourceClass . }
    UNION
    { 
        ?sourceWithFK a domain:SourceClass ;
            domain:SourceClass.foreignKeyProperty ?fk .
        ?target a domain:TargetClass ;
            domain:TargetClass.idProperty ?fk .
    }
}
```

**Expected Coverage Calculation**:
- If `sourcesWithFK` / `totalSources` ≈ link count / `totalSources` → Good!
- If big discrepancy → Either cartesian product or missing filters

**Before Proceeding Checklist**:
- [ ] Total link count makes business sense (not orders of magnitude too high/low)
- [ ] Link count ≈ number of source entities (allowing for orphaned references)
- [ ] No cartesian product detected (links ≠ sources × targets)
- [ ] Orphaned references documented and understood
- [ ] Coverage percentage calculated and reasonable (typically 60-100%)

---

### Step 6: Add Transformation Steps

Once SELECT query is validated, convert to INSERT:

```bash
mcp_ags-sparql-ag_add_transformation_step
- layer_name_or_uri: "{Domain} Internal Linking"
- step_name: "Link {Source} to {Target}"
- insert_query: "..." # See template below
- explanation: "Linking {source} to {target} using {matching_property} matching"
```

#### Transformation Query Template
```sparql
PREFIX domain: <{SOURCE_ONTOLOGY_URI}#>
PREFIX linking: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#>

INSERT {
    GRAPH ${targetGraph} {
        ?source linking:{propertyName} ?target .
    }
}
${usingSources}
WHERE {
    # Use EXACT WHERE clause from validated SELECT query
    ?source a domain:SourceClass ;
        domain:SourceClass.foreignKeyProperty ?matchingValue .
    ?target a domain:TargetClass ;
        domain:TargetClass.idProperty ?matchingValue .
}
```

**Critical Template Requirements**:
- Use `${targetGraph}` (single $, not $$)
- Use `${usingSources}` (single $, not $$)
- Use `\\n` for line breaks (not `\\\\n`)
- Copy exact WHERE clause from validated SELECT query

---

### Step 7: Execute Linking Transformations

#### 7.1 Refresh Graphmart (ALWAYS - Unless User Explicitly Requests Reload)
```bash
mcp_ags-sparql-ag_refresh_graphmart
- explanation: "Refreshing graphmart to execute {domain} internal linking transformations"
```

**🚨 CRITICAL RULE: Refresh vs Reload**

**ALWAYS use `refresh_graphmart`** unless the user explicitly asks for reload:
- ✅ **Refresh**: Fast (seconds to ~1 minute), only processes dirty/changed layers
  - Use for: All linking transformations, step updates, property additions
  
- ❌ **Reload**: Slow (minutes to hours), rebuilds ALL layers from scratch
  - Use ONLY when: User explicitly requests it, or catastrophic errors in graphmart
  - Why avoid: Wastes time, no benefit for incremental linking work

**Execution Time Indicators**:
- 0.5-2 seconds: No actual changes (validation refresh)
- 5-30 seconds: Actual transformation work happening (good!)
- >1 minute: Large dataset or multiple layers being processed

**Never say**: "Should I refresh or reload?"  
**Always say**: "Refreshing graphmart..." (refresh is the default)

#### 7.2 Check Layer Status (if needed)
```bash
mcp_ags-sparql-ag_get_layer_status
- layer_name_or_uri: "{LAYER_URI}"
- explanation: "Checking if linking layer executed successfully"
```

**Success Indicators**:
- `layer_status`: "Online"
- `is_structure_valid`: true
- No errors in step details

---

### Step 8: Validate Results

#### 8.1 Count New Links

**IMPORTANT**: Count each link type separately for better performance.

```sparql
PREFIX linking: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#>

# Count links for specific property
SELECT (COUNT(*) as ?linkCount)
WHERE {
    ?source linking:{propertyName} ?target .
}
```

**Best Practice**: Run a separate query for each linking property rather than combining them. This is faster and provides clearer results.

**Expected Results**: Should match or be close to the SELECT query counts from Step 5.

#### 8.2 Test Business Queries
```sparql
PREFIX domain: <{SOURCE_ONTOLOGY_URI}#>
PREFIX linking: <{YOUR_BASE_URI}/ontologies/{SHORT_UUID}/{Domain}Linking#>

# Example: Get all related entities for a specific entity
SELECT ?sourceName ?targetName
WHERE {
    ?source a domain:SourceClass ;
        domain:SourceClass.nameProperty ?sourceName ;
        linking:{propertyName} ?target .
    ?target domain:TargetClass.nameProperty ?targetName .
}
ORDER BY ?sourceName
LIMIT 10
```

**Goal**: Demonstrate that you can now navigate relationships using object properties instead of string matching.

#### 8.3 Calculate Coverage
```sparql
# Calculate linking coverage percentage
SELECT 
    (COUNT(DISTINCT ?source) as ?totalSources)
    (COUNT(DISTINCT ?linkedSource) as ?linkedSources)
    ((?linkedSources * 100 / ?totalSources) as ?coveragePercent)
WHERE {
    {
        ?source a domain:SourceClass .
    }
    UNION
    {
        ?linkedSource a domain:SourceClass ;
            linking:{propertyName} ?target .
    }
}
```

**Success Criteria**: 70%+ coverage is good (some orphaned references are expected).

---

## 📊 Success Metrics

### Linking Coverage
- ✅ **80%+ of entities linked** - Excellent
- ✅ **60-80% of entities linked** - Good (expected with real-world data)
- ⚠️ **40-60% of entities linked** - Review data quality
- ❌ **<40% of entities linked** - Check query logic or data issues

### Query Performance
- Object property navigation should be faster than string matching
- Queries using linking properties should return results in <2 seconds

### Business Value
Document specific queries enabled, such as:
- "Show all opportunities for customer X" (without string matching)
- "Find all feedback for equipment Y" (direct navigation)
- "Calculate customer satisfaction across all feedback" (aggregation)

---

## 🚨 Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| **0 results from linking query** | Verify property names match exactly (case-sensitive) |
| **Forgot to register ontology** | Links won't work; run `register_ontology` then refresh |
| **Forgot to import source ontology** | Properties can't reference classes; add import statement |
| **Template syntax errors** | Use `${targetGraph}` and `${usingSources}` (single $) |
| **Transformation step failed** | Check layer status for error details; fix query and update step |
| **Cartesian product explosion** | Add proper FILTER conditions, validate with COUNT first |
| **Low coverage** | Check data quality, property name mismatches, or missing data |
| **Performance issues** | Index foreign key properties if possible in source system |

---

## 🎯 Quick Reference Template

**Replace these placeholders in all examples**:
- `{YOUR_BASE_URI}` - Your organization's base URI (e.g., `http://company.com`)
- `{SHORT_UUID}` - 8-character hex UUID for global uniqueness (e.g., `a3f9c2e1`)
- `{Domain}` - Domain name (e.g., `CRM`, `ERP`, `PLM`)
- `{SOURCE_ONTOLOGY_URI}` - The auto-generated layer ontology URI
- `{LAYER_URI}` - The transformation layer URI
- `{propertyName}` - Your linking property name
- `{SourceClass}` / `{TargetClass}` - Entity class names
- `{matching_property}` - The foreign key property used for matching

**Generate UUID**: Simply create an 8-character hex string (e.g., `7f3a2c91`, `b4e8d1f6`, `9c2a5e73`). Any random combination of hex digits (0-9, a-f) will work - the key is uniqueness within your graphmart environment.

**Example URIs**:
- Linking Ontology: `http://company.com/ontologies/a3f9c2e1/CRMLinking`
- Property: `http://company.com/ontologies/a3f9c2e1/CRMLinking#relatedCustomer`
- Layer: "CRM Internal Linking"
"""

    @mcp.prompt()
    def troubleshooting_guide() -> str:
        """Common issues and solutions."""
        return """# Anzo MCP Troubleshooting Guide

## Connection Issues

### Cannot Connect to Anzo
1. Check .env file has correct credentials
2. Verify ANZO_HTTP_BASE is accessible
3. Test: `list_graphmarts` should return list

### 401 Authentication Error
- Wrong username/password in .env
- Check ANZO_USERNAME and ANZO_PASSWORD

### 404 Not Found
- Graphmart/resource doesn't exist
- Check URI spelling (case-sensitive!)
- Verify you have permissions

## Query Issues

### SPARQL Query Returns Empty
1. Check graphmart is activated
2. Verify you're querying correct graphmart_uri
3. Test simple query: `SELECT * WHERE {?s ?p ?o} LIMIT 10`

### Query Timeout
- Add LIMIT to constrain results
- Simplify complex joins
- Check graphmart status (may be slow if loading)

### Invalid Query Syntax
- Validate SPARQL syntax
- Check prefix declarations
- Use sparql_query_guide prompt for examples

## Performance Issues

### Slow Queries
1. Add appropriate LIMIT
2. Use indexes: query by known URIs
3. Place FILTERs early in WHERE clause
4. Avoid OPTIONAL when possible

### Graphmart Won't Activate
- Check graphmart status first
- May already be activating (wait 60s)
- Check server resources
- Try refresh instead of reload

## Data Issues

### Data Not Showing in Queries
1. Verify layer is in graphmart
2. Check layer order (top layers override)
3. Ensure dataset has ACLs allowing read
4. Confirm data uploaded successfully

### Upload Fails
- Check file format matches content
- Validate RDF syntax before upload
- Split large files (>100MB)
- Verify dataset exists first

## Getting Help

1. Check graphmart status: `retrieve_graphmart_status`
2. List available resources: `list_graphmarts`
3. Test with simple operations first
4. Check Anzo server logs if available

Always start with simplest operation and build up!
"""
