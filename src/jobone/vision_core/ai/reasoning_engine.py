"""
🧠 Orion Vision Core - Advanced AI Reasoning Engine
Chain-of-thought processing and multi-step problem solving

This module provides advanced reasoning capabilities:
- Chain-of-thought processing
- Multi-step problem decomposition
- Logical reasoning and inference
- Decision tree generation and optimization
- Complex problem solving workflows

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import re

from .multi_model_manager import MultiModelManager, ModelCapability, AIResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    """Types of reasoning approaches"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STEP_BY_STEP = "step_by_step"
    PROBLEM_DECOMPOSITION = "problem_decomposition"
    LOGICAL_INFERENCE = "logical_inference"
    DECISION_TREE = "decision_tree"
    CAUSAL_REASONING = "causal_reasoning"
    ANALOGICAL_REASONING = "analogical_reasoning"

class ReasoningStep(Enum):
    """Individual reasoning step types"""
    ANALYSIS = "analysis"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    CONCLUSION = "conclusion"
    QUESTION = "question"
    ASSUMPTION = "assumption"
    VERIFICATION = "verification"

@dataclass
class ReasoningNode:
    """Individual step in reasoning process"""
    step_id: str
    step_type: ReasoningStep
    content: str
    confidence: float
    dependencies: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ReasoningChain:
    """Complete reasoning chain with multiple steps"""
    chain_id: str
    reasoning_type: ReasoningType
    original_problem: str
    steps: List[ReasoningNode] = field(default_factory=list)
    final_conclusion: str = ""
    confidence_score: float = 0.0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ReasoningConfig:
    """Configuration for reasoning engine"""
    max_steps: int = 10
    min_confidence_threshold: float = 0.7
    enable_verification: bool = True
    enable_self_correction: bool = True
    reasoning_depth: int = 3
    parallel_reasoning: bool = False
    timeout_seconds: float = 60.0

class ReasoningEngine:
    """
    Advanced AI reasoning engine for Orion Vision Core.

    Provides sophisticated reasoning capabilities:
    - Chain-of-thought processing
    - Multi-step problem solving
    - Logical inference and verification
    - Decision tree generation
    """

    def __init__(self, multi_model_manager: MultiModelManager, config: Optional[ReasoningConfig] = None):
        """Initialize the reasoning engine"""
        self.multi_model_manager = multi_model_manager
        self.config = config or ReasoningConfig()
        self.reasoning_history: List[ReasoningChain] = []
        self.reasoning_templates = self._load_reasoning_templates()

        logger.info("🧠 Advanced AI Reasoning Engine initialized")

    def _load_reasoning_templates(self) -> Dict[str, str]:
        """Load reasoning prompt templates"""
        return {
            ReasoningType.CHAIN_OF_THOUGHT.value: """
Let's think through this step by step using chain-of-thought reasoning.

Problem: {problem}

Please provide a detailed reasoning process with the following structure:
1. Initial Analysis: What is the core problem?
2. Key Components: What are the main elements to consider?
3. Step-by-step reasoning: Work through the logic systematically
4. Evidence and assumptions: What evidence supports each step?
5. Final conclusion: What is the most logical conclusion?

Think carefully and show your reasoning process clearly.
""",

            ReasoningType.PROBLEM_DECOMPOSITION.value: """
Let's break down this complex problem into smaller, manageable parts.

Problem: {problem}

Please decompose this problem using the following approach:
1. Problem Analysis: Identify the main problem and its scope
2. Subproblem Identification: Break it into smaller, solvable parts
3. Dependencies: Identify relationships between subproblems
4. Solution Strategy: Propose approach for each subproblem
5. Integration Plan: How to combine solutions

Provide a systematic decomposition.
""",

            ReasoningType.LOGICAL_INFERENCE.value: """
Let's apply logical reasoning and inference to solve this problem.

Problem: {problem}

Please use logical inference with this structure:
1. Given Facts: What information do we have?
2. Logical Rules: What principles or rules apply?
3. Inference Steps: Apply logical reasoning step by step
4. Validity Check: Verify the logical consistency
5. Conclusion: What can we logically conclude?

Use formal logical reasoning where possible.
""",

            ReasoningType.DECISION_TREE.value: """
Let's create a decision tree to analyze this problem systematically.

Problem: {problem}

Please create a decision tree analysis:
1. Root Question: What is the main decision point?
2. Decision Criteria: What factors influence the decision?
3. Branch Analysis: Explore different paths and outcomes
4. Probability Assessment: Evaluate likelihood of outcomes
5. Optimal Path: Recommend the best decision path

Structure this as a clear decision tree.
"""
        }

    async def reason_through_problem(self, problem: str, reasoning_type: ReasoningType = ReasoningType.CHAIN_OF_THOUGHT) -> ReasoningChain:
        """Main reasoning function that processes a problem through advanced reasoning"""

        start_time = asyncio.get_event_loop().time()

        logger.info(f"🧠 Starting {reasoning_type.value} reasoning for problem...")

        # Create reasoning chain
        chain = ReasoningChain(
            chain_id=f"reasoning_{int(start_time * 1000)}",
            reasoning_type=reasoning_type,
            original_problem=problem
        )

        try:
            if reasoning_type == ReasoningType.CHAIN_OF_THOUGHT:
                await self._chain_of_thought_reasoning(chain)
            elif reasoning_type == ReasoningType.PROBLEM_DECOMPOSITION:
                await self._problem_decomposition_reasoning(chain)
            elif reasoning_type == ReasoningType.LOGICAL_INFERENCE:
                await self._logical_inference_reasoning(chain)
            elif reasoning_type == ReasoningType.DECISION_TREE:
                await self._decision_tree_reasoning(chain)
            else:
                # Default to chain of thought
                await self._chain_of_thought_reasoning(chain)

            # Calculate final confidence and processing time
            chain.confidence_score = self._calculate_chain_confidence(chain)
            chain.processing_time = asyncio.get_event_loop().time() - start_time

            # Verify reasoning if enabled
            if self.config.enable_verification:
                await self._verify_reasoning_chain(chain)

            # Store in history
            self.reasoning_history.append(chain)

            logger.info(f"✅ Reasoning completed: {len(chain.steps)} steps, "
                       f"confidence={chain.confidence_score:.2f}, "
                       f"time={chain.processing_time:.2f}s")

            return chain

        except Exception as e:
            logger.error(f"❌ Reasoning failed: {e}")
            chain.metadata['error'] = str(e)
            chain.processing_time = asyncio.get_event_loop().time() - start_time
            return chain

    async def _chain_of_thought_reasoning(self, chain: ReasoningChain):
        """Implement chain-of-thought reasoning"""

        # Get reasoning template
        template = self.reasoning_templates[ReasoningType.CHAIN_OF_THOUGHT.value]
        prompt = template.format(problem=chain.original_problem)

        # Generate initial reasoning response
        response = await self.multi_model_manager.generate_response(
            prompt,
            ModelCapability.REASONING
        )

        if not response:
            raise Exception("Failed to generate initial reasoning response")

        # Parse reasoning steps from response
        steps = self._parse_reasoning_steps(response.response_text, ReasoningType.CHAIN_OF_THOUGHT)
        chain.steps.extend(steps)

        # Generate follow-up questions and deeper analysis
        if len(steps) > 0:
            await self._generate_follow_up_analysis(chain)

        # Generate final conclusion
        await self._generate_final_conclusion(chain)

    async def _problem_decomposition_reasoning(self, chain: ReasoningChain):
        """Implement problem decomposition reasoning"""

        template = self.reasoning_templates[ReasoningType.PROBLEM_DECOMPOSITION.value]
        prompt = template.format(problem=chain.original_problem)

        response = await self.multi_model_manager.generate_response(
            prompt,
            ModelCapability.ANALYSIS
        )

        if not response:
            raise Exception("Failed to generate decomposition response")

        # Parse decomposition steps
        steps = self._parse_reasoning_steps(response.response_text, ReasoningType.PROBLEM_DECOMPOSITION)
        chain.steps.extend(steps)

        # Analyze each subproblem
        await self._analyze_subproblems(chain)

        # Generate integration strategy
        await self._generate_integration_strategy(chain)

    async def _logical_inference_reasoning(self, chain: ReasoningChain):
        """Implement logical inference reasoning"""

        template = self.reasoning_templates[ReasoningType.LOGICAL_INFERENCE.value]
        prompt = template.format(problem=chain.original_problem)

        response = await self.multi_model_manager.generate_response(
            prompt,
            ModelCapability.REASONING
        )

        if not response:
            raise Exception("Failed to generate logical inference response")

        # Parse logical steps
        steps = self._parse_reasoning_steps(response.response_text, ReasoningType.LOGICAL_INFERENCE)
        chain.steps.extend(steps)

        # Verify logical consistency
        await self._verify_logical_consistency(chain)

    async def _decision_tree_reasoning(self, chain: ReasoningChain):
        """Implement decision tree reasoning"""

        template = self.reasoning_templates[ReasoningType.DECISION_TREE.value]
        prompt = template.format(problem=chain.original_problem)

        response = await self.multi_model_manager.generate_response(
            prompt,
            ModelCapability.ANALYSIS
        )

        if not response:
            raise Exception("Failed to generate decision tree response")

        # Parse decision tree
        steps = self._parse_reasoning_steps(response.response_text, ReasoningType.DECISION_TREE)
        chain.steps.extend(steps)

        # Analyze decision paths
        await self._analyze_decision_paths(chain)

    def _parse_reasoning_steps(self, response_text: str, reasoning_type: ReasoningType) -> List[ReasoningNode]:
        """Parse reasoning steps from AI response"""

        steps = []

        # Simple parsing based on numbered lists and common patterns
        lines = response_text.split('\n')
        current_step = None
        step_counter = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for numbered steps or section headers
            if re.match(r'^\d+\.', line) or any(keyword in line.lower() for keyword in ['analysis:', 'conclusion:', 'evidence:', 'step']):
                if current_step:
                    steps.append(current_step)

                step_counter += 1
                step_type = self._determine_step_type(line)

                current_step = ReasoningNode(
                    step_id=f"step_{step_counter}",
                    step_type=step_type,
                    content=line,
                    confidence=0.8  # Default confidence
                )
            elif current_step:
                # Continue building current step content
                current_step.content += " " + line

        # Add the last step
        if current_step:
            steps.append(current_step)

        return steps

    def _determine_step_type(self, text: str) -> ReasoningStep:
        """Determine the type of reasoning step based on content"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['analysis', 'analyze', 'examine']):
            return ReasoningStep.ANALYSIS
        elif any(word in text_lower for word in ['hypothesis', 'assume', 'suppose']):
            return ReasoningStep.HYPOTHESIS
        elif any(word in text_lower for word in ['evidence', 'proof', 'support']):
            return ReasoningStep.EVIDENCE
        elif any(word in text_lower for word in ['conclusion', 'conclude', 'therefore']):
            return ReasoningStep.CONCLUSION
        elif any(word in text_lower for word in ['question', 'ask', 'what if']):
            return ReasoningStep.QUESTION
        else:
            return ReasoningStep.ANALYSIS  # Default

    async def _generate_follow_up_analysis(self, chain: ReasoningChain):
        """Generate follow-up analysis for deeper reasoning"""

        if not chain.steps:
            return

        # Create follow-up prompt based on existing steps
        follow_up_prompt = f"""
Based on the initial reasoning about: {chain.original_problem}

Previous analysis: {chain.steps[-1].content[:200]}...

Please provide deeper analysis by:
1. Identifying potential weaknesses in the reasoning
2. Considering alternative perspectives
3. Exploring edge cases or exceptions
4. Strengthening the logical connections

Provide additional insights and analysis.
"""

        response = await self.multi_model_manager.generate_response(
            follow_up_prompt,
            ModelCapability.ANALYSIS
        )

        if response:
            follow_up_step = ReasoningNode(
                step_id=f"followup_{len(chain.steps) + 1}",
                step_type=ReasoningStep.ANALYSIS,
                content=response.response_text,
                confidence=0.75,
                dependencies=[chain.steps[-1].step_id] if chain.steps else []
            )
            chain.steps.append(follow_up_step)

    async def _generate_final_conclusion(self, chain: ReasoningChain):
        """Generate final conclusion based on all reasoning steps"""

        if not chain.steps:
            chain.final_conclusion = "Unable to reach conclusion due to insufficient reasoning steps."
            return

        # Summarize all steps for conclusion
        steps_summary = "\n".join([f"{i+1}. {step.content[:100]}..." for i, step in enumerate(chain.steps)])

        conclusion_prompt = f"""
Based on the complete reasoning process for: {chain.original_problem}

Reasoning steps:
{steps_summary}

Please provide a clear, concise final conclusion that:
1. Synthesizes all the reasoning steps
2. Addresses the original problem directly
3. Acknowledges any limitations or uncertainties
4. Provides actionable insights if applicable

Final conclusion:
"""

        response = await self.multi_model_manager.generate_response(
            conclusion_prompt,
            ModelCapability.ANALYSIS
        )

        if response:
            chain.final_conclusion = response.response_text

            # Add conclusion as final step
            conclusion_step = ReasoningNode(
                step_id=f"conclusion_{len(chain.steps) + 1}",
                step_type=ReasoningStep.CONCLUSION,
                content=response.response_text,
                confidence=0.85,
                dependencies=[step.step_id for step in chain.steps]
            )
            chain.steps.append(conclusion_step)

    async def _analyze_subproblems(self, chain: ReasoningChain):
        """Analyze individual subproblems in decomposition"""

        # Find decomposition steps
        decomp_steps = [step for step in chain.steps if "subproblem" in step.content.lower()]

        for step in decomp_steps:
            subproblem_prompt = f"""
Analyze this specific subproblem in detail:
{step.content}

Provide:
1. Detailed analysis of this subproblem
2. Potential solutions or approaches
3. Resources or information needed
4. Estimated complexity and effort
5. Dependencies on other subproblems

Focus specifically on this subproblem.
"""

            response = await self.multi_model_manager.generate_response(
                subproblem_prompt,
                ModelCapability.ANALYSIS
            )

            if response:
                analysis_step = ReasoningNode(
                    step_id=f"subanalysis_{len(chain.steps) + 1}",
                    step_type=ReasoningStep.ANALYSIS,
                    content=response.response_text,
                    confidence=0.8,
                    dependencies=[step.step_id]
                )
                chain.steps.append(analysis_step)

    async def _generate_integration_strategy(self, chain: ReasoningChain):
        """Generate strategy for integrating subproblem solutions"""

        integration_prompt = f"""
Based on the problem decomposition for: {chain.original_problem}

All subproblems and analyses have been identified. Now provide an integration strategy that:
1. Defines the order of solving subproblems
2. Identifies critical dependencies
3. Suggests coordination mechanisms
4. Outlines risk mitigation strategies
5. Provides a timeline or roadmap

Create a comprehensive integration plan.
"""

        response = await self.multi_model_manager.generate_response(
            integration_prompt,
            ModelCapability.ANALYSIS
        )

        if response:
            integration_step = ReasoningNode(
                step_id=f"integration_{len(chain.steps) + 1}",
                step_type=ReasoningStep.ANALYSIS,
                content=response.response_text,
                confidence=0.8
            )
            chain.steps.append(integration_step)

    async def _verify_logical_consistency(self, chain: ReasoningChain):
        """Verify logical consistency of reasoning chain"""

        if len(chain.steps) < 2:
            return

        verification_prompt = f"""
Please verify the logical consistency of this reasoning chain:

Original problem: {chain.original_problem}

Reasoning steps:
{chr(10).join([f"{i+1}. {step.content}" for i, step in enumerate(chain.steps)])}

Check for:
1. Logical consistency between steps
2. Valid inferences and conclusions
3. Potential logical fallacies
4. Missing logical connections
5. Overall coherence

Provide a logical consistency assessment.
"""

        response = await self.multi_model_manager.generate_response(
            verification_prompt,
            ModelCapability.REASONING
        )

        if response:
            verification_step = ReasoningNode(
                step_id=f"verification_{len(chain.steps) + 1}",
                step_type=ReasoningStep.VERIFICATION,
                content=response.response_text,
                confidence=0.9
            )
            chain.steps.append(verification_step)

    async def _analyze_decision_paths(self, chain: ReasoningChain):
        """Analyze different decision paths in decision tree"""

        decision_prompt = f"""
Based on the decision tree analysis for: {chain.original_problem}

Please analyze the decision paths by:
1. Evaluating pros and cons of each major path
2. Assessing risks and opportunities
3. Considering resource requirements
4. Analyzing potential outcomes
5. Recommending the optimal decision path

Provide detailed path analysis and recommendations.
"""

        response = await self.multi_model_manager.generate_response(
            decision_prompt,
            ModelCapability.ANALYSIS
        )

        if response:
            path_analysis_step = ReasoningNode(
                step_id=f"path_analysis_{len(chain.steps) + 1}",
                step_type=ReasoningStep.ANALYSIS,
                content=response.response_text,
                confidence=0.8
            )
            chain.steps.append(path_analysis_step)

    async def _verify_reasoning_chain(self, chain: ReasoningChain):
        """Verify the overall reasoning chain quality"""

        if not chain.steps:
            return

        verification_prompt = f"""
Please evaluate the quality and completeness of this reasoning process:

Problem: {chain.original_problem}
Reasoning Type: {chain.reasoning_type.value}
Number of Steps: {len(chain.steps)}

Final Conclusion: {chain.final_conclusion}

Evaluate:
1. Completeness of the reasoning process
2. Quality of individual reasoning steps
3. Logical flow and coherence
4. Adequacy of the final conclusion
5. Overall reasoning quality (score 1-10)

Provide quality assessment and suggestions for improvement.
"""

        response = await self.multi_model_manager.generate_response(
            verification_prompt,
            ModelCapability.ANALYSIS
        )

        if response:
            # Extract quality score if possible
            quality_score = self._extract_quality_score(response.response_text)
            chain.metadata['quality_assessment'] = response.response_text
            chain.metadata['quality_score'] = quality_score

    def _extract_quality_score(self, assessment_text: str) -> float:
        """Extract quality score from assessment text"""

        # Look for patterns like "score: 8/10", "8 out of 10", "quality: 7.5"
        import re

        patterns = [
            r'score[:\s]+(\d+(?:\.\d+)?)[/\s]*(?:out of\s*)?10',
            r'(\d+(?:\.\d+)?)[/\s]*(?:out of\s*)?10',
            r'quality[:\s]+(\d+(?:\.\d+)?)'
        ]

        for pattern in patterns:
            match = re.search(pattern, assessment_text.lower())
            if match:
                try:
                    score = float(match.group(1))
                    return min(score / 10.0, 1.0) if score > 1.0 else score
                except ValueError:
                    continue

        return 0.7  # Default score

    def _calculate_chain_confidence(self, chain: ReasoningChain) -> float:
        """Calculate overall confidence score for reasoning chain"""

        if not chain.steps:
            return 0.0

        # Average confidence of all steps
        step_confidences = [step.confidence for step in chain.steps]
        avg_confidence = sum(step_confidences) / len(step_confidences)

        # Adjust based on number of steps (more steps can mean more thorough reasoning)
        step_bonus = min(len(chain.steps) * 0.05, 0.2)  # Max 20% bonus

        # Adjust based on verification if available
        verification_bonus = 0.1 if any(step.step_type == ReasoningStep.VERIFICATION for step in chain.steps) else 0

        final_confidence = min(avg_confidence + step_bonus + verification_bonus, 1.0)
        return final_confidence

    def get_reasoning_history(self, limit: int = 10) -> List[ReasoningChain]:
        """Get recent reasoning history"""
        return self.reasoning_history[-limit:] if self.reasoning_history else []

    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning engine statistics"""

        if not self.reasoning_history:
            return {
                'total_reasoning_chains': 0,
                'average_confidence': 0.0,
                'average_steps': 0.0,
                'average_processing_time': 0.0,
                'reasoning_types_used': []
            }

        total_chains = len(self.reasoning_history)
        avg_confidence = sum(chain.confidence_score for chain in self.reasoning_history) / total_chains
        avg_steps = sum(len(chain.steps) for chain in self.reasoning_history) / total_chains
        avg_time = sum(chain.processing_time for chain in self.reasoning_history) / total_chains

        reasoning_types = list(set(chain.reasoning_type.value for chain in self.reasoning_history))

        return {
            'total_reasoning_chains': total_chains,
            'average_confidence': avg_confidence,
            'average_steps': avg_steps,
            'average_processing_time': avg_time,
            'reasoning_types_used': reasoning_types,
            'supported_reasoning_types': [rt.value for rt in ReasoningType]
        }
