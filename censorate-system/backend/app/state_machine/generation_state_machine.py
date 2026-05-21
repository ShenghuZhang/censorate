"""State machine for the code generation pipeline."""


class GenerationState:
    """Pipeline state constants."""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    DESIGNING = "designing"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    READY = "ready"
    PUSHING = "pushing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationStateMachine:
    """State machine for the code generation pipeline."""

    TRANSITIONS = {
        GenerationState.DRAFT: [GenerationState.CONFIRMED, GenerationState.FAILED],
        GenerationState.CONFIRMED: [GenerationState.DESIGNING, GenerationState.DRAFT, GenerationState.FAILED],
        GenerationState.DESIGNING: [GenerationState.GENERATING, GenerationState.CONFIRMED, GenerationState.FAILED],
        GenerationState.GENERATING: [GenerationState.REVIEWING, GenerationState.DESIGNING, GenerationState.FAILED],
        GenerationState.REVIEWING: [GenerationState.READY, GenerationState.GENERATING, GenerationState.FAILED],
        GenerationState.READY: [GenerationState.PUSHING, GenerationState.REVIEWING, GenerationState.FAILED],
        GenerationState.PUSHING: [GenerationState.COMPLETED, GenerationState.READY, GenerationState.FAILED],
        GenerationState.FAILED: [GenerationState.DRAFT, GenerationState.CONFIRMED],
    }

    @staticmethod
    def can_transition(from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid."""
        return to_state in GenerationStateMachine.TRANSITIONS.get(from_state, [])

    @staticmethod
    def is_terminal(state: str) -> bool:
        """Check if state is a terminal state."""
        return state in [GenerationState.COMPLETED, GenerationState.FAILED]

    @staticmethod
    def is_retryable(state: str) -> bool:
        """Check if a retry is possible from this state."""
        return state in [GenerationState.FAILED]
