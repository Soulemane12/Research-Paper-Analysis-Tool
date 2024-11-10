import time
import yaml
import json
import os
from dotenv import load_dotenv
from julep import Julep

# Load environment variables
load_dotenv()

# Get API key from environment variable
client = Julep(api_key=os.getenv('JULEP_API_KEY'))

def create_agent():
    print("Creating Julep agent...")
    agent = client.agents.create(
        name="Research Insights Agent",
        model="o1-preview",
        about="You extract research questions, claims, evidence, and contextualize claims from complex research papers."
    )
    
    return agent

agent = create_agent()

def create_task():
    print("Creating Julep task...")
    task_yaml = """
    name: Research Extractor
    description: Extract key insights from a research paper, including the research question, claims, evidence, and contextualized claims.

    main:
      - prompt:
          - role: system
            content: You are an AI specialized in analyzing research papers.
          - role: user
            content: >
              Please analyze the following research paper text and extract:
              1. The main research question.
              2. Key claims made in the paper.
              3. Evidence supporting those claims.
              4. Provide a claim along with its context.

              Text:
              {{_.research_text}}

              Return the results in the following JSON structure:
              ```json
              {
                "research_question": "<string>",
                "claims": ["<string>", "<string>"],
                "evidence": ["<string>", "<string>"],
                "claim_with_context": "<string>"
              }
              ```
        unwrap: true
    """
    task = client.tasks.create(
        agent_id=agent.id,
        **yaml.safe_load(task_yaml)
    )
    print("Task created successfully.")
    return task

task = create_task()

def process_with_julep(text):
    print("Starting Julep task execution...")
    try:
        execution = client.executions.create(
            task_id=task.id,
            input={"research_text": text}
        )

        while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
            print(f"Current status: {result.status}... waiting.")
            time.sleep(1)

        if result.status == 'succeeded':
            print("Task succeeded. Raw output:", result.output)
            try:
                # Try to clean and parse the output
                output_str = result.output.strip()
                if output_str.startswith('```json'):
                    output_str = output_str[7:]  # Remove ```json prefix
                if output_str.endswith('```'):
                    output_str = output_str[:-3]  # Remove ``` suffix
                
                parsed_result = json.loads(output_str)
                print("Successfully parsed JSON:", parsed_result)
                return parsed_result
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw output that failed to parse: {result.output}")
                # Return a structured error response
                return {
                    "error": "Failed to parse response",
                    "research_question": "Error parsing response",
                    "claims": [],
                    "evidence": [],
                    "claim_with_context": "Error parsing response"
                }
        else:
            print(f"Task failed with error: {result.error}")
            return {
                "error": str(result.error),
                "research_question": "Task execution failed",
                "claims": [],
                "evidence": [],
                "claim_with_context": "Task execution failed"
            }
            
    except Exception as e:
        print(f"Unexpected error in process_with_julep: {str(e)}")
        return {
            "error": str(e),
            "research_question": "Unexpected error occurred",
            "claims": [],
            "evidence": [],
            "claim_with_context": "Unexpected error occurred"
        }

def semantic_similarity_check(text1, text2):
    """Calculate semantic similarity between two text strings."""
    try:
        # Simple text matching approach since Julep doesn't have embeddings
        text1_words = set(text1.lower().split())
        text2_words = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(text1_words.intersection(text2_words))
        union = len(text1_words.union(text2_words))
        
        similarity = intersection / union if union > 0 else 0
        return similarity
        
    except Exception as e:
        print(f"Error in semantic similarity check: {e}")
        return 0

def cross_reference_claims(results):
    """Find and organize cross-references between papers."""
    cross_references = []
    
    # Key topics to track
    topics = {
        'initial_findings': ['initial', 'first', 'original', 'kosfeld'],
        'replication': ['replicate', 'replication', 'failed', 'attempt'],
        'social_contact': ['social contact', 'social interaction', 'social cue'],
        'methodology': ['method', 'measurement', 'plasma', 'extraction']
    }
    
    for i, paper1 in enumerate(results):
        for claim in paper1.get('claims', []):
            supporting_evidence = []
            contradicting_evidence = []
            
            # Identify the topic of the claim
            claim_topics = set()
            for topic, keywords in topics.items():
                if any(keyword.lower() in claim.lower() for keyword in keywords):
                    claim_topics.add(topic)
            
            if not claim_topics:
                continue
                
            # Look for related evidence in other papers
            for j, paper2 in enumerate(results):
                if i == j:
                    continue
                    
                for evidence in paper2.get('evidence', []):
                    # Check if evidence relates to same topics
                    evidence_topics = set()
                    for topic, keywords in topics.items():
                        if any(keyword.lower() in evidence.lower() for keyword in keywords):
                            evidence_topics.add(topic)
                    
                    if claim_topics & evidence_topics:  # If there's topic overlap
                        # Determine if supporting or contradicting
                        is_contradicting = any(word in evidence.lower() for word in 
                            ['not', 'fail', 'no effect', 'unreliable', 'flawed'])
                        
                        if is_contradicting:
                            contradicting_evidence.append({
                                'paper': paper2['filename'],
                                'evidence': evidence
                            })
                        else:
                            supporting_evidence.append({
                                'paper': paper2['filename'],
                                'evidence': evidence
                            })
            
            if supporting_evidence or contradicting_evidence:
                cross_references.append({
                    'source_paper': paper1['filename'],
                    'claim': claim,
                    'supporting_evidence': supporting_evidence,
                    'contradicting_evidence': contradicting_evidence
                })
    
    return cross_references

def analyze_discourse_relationships(results):
    """Analyze and structure relationships between claims and evidence for visualization."""
    discourse_graph = {
        'nodes': [],
        'edges': []
    }
    
    node_id = 0
    node_map = {}  # Maps claims/evidence to node IDs
    
    # First pass: Create nodes
    for paper in results:
        # Add research question node
        q_node = {
            'id': node_id,
            'type': 'question',
            'label': paper['research_question'],
            'paper': paper['filename']
        }
        discourse_graph['nodes'].append(q_node)
        question_id = node_id
        node_id += 1
        
        # Add claim nodes
        for claim in paper.get('claims', []):
            claim_node = {
                'id': node_id,
                'type': 'claim',
                'label': claim,
                'paper': paper['filename']
            }
            discourse_graph['nodes'].append(claim_node)
            node_map[claim] = node_id
            
            # Link claim to research question
            discourse_graph['edges'].append({
                'source': question_id,
                'target': node_id,
                'type': 'addresses'
            })
            node_id += 1
            
        # Add evidence nodes
        for evidence in paper.get('evidence', []):
            evidence_node = {
                'id': node_id,
                'type': 'evidence',
                'label': evidence,
                'paper': paper['filename']
            }
            discourse_graph['nodes'].append(evidence_node)
            node_map[evidence] = node_id
            node_id += 1
    
    # Second pass: Create edges between claims and evidence
    for ref in cross_reference_claims(results):
        claim_id = node_map.get(ref['claim'])
        if claim_id is None:
            continue
            
        # Add supporting evidence edges
        for evidence in ref.get('supporting_evidence', []):
            evidence_id = node_map.get(evidence['evidence'])
            if evidence_id is not None:
                discourse_graph['edges'].append({
                    'source': evidence_id,
                    'target': claim_id,
                    'type': 'supports'
                })
        
        # Add contradicting evidence edges
        for evidence in ref.get('contradicting_evidence', []):
            evidence_id = node_map.get(evidence['evidence'])
            if evidence_id is not None:
                discourse_graph['edges'].append({
                    'source': evidence_id,
                    'target': claim_id,
                    'type': 'contradicts'
                })
    
    return discourse_graph
