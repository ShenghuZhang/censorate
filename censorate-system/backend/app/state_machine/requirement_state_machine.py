class RequirementState:
    """Requirement state constants."""
    NEW = "new"
    ANALYSIS = "analysis"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    COMPLETED = "completed"

    # New simplified states
    BACKLOG = "backlog"
    TODO = "todo"
    IN_REVIEW = "in_review"
    DONE = "done"


class RequirementStateMachine:
    """Requirement state machine with transition logic."""

    NON_TECHNICAL_TRANSITIONS = {
        RequirementState.NEW: [RequirementState.ANALYSIS],
        RequirementState.ANALYSIS: [RequirementState.DESIGN, RequirementState.NEW],
        RequirementState.DESIGN: [RequirementState.ANALYSIS, RequirementState.COMPLETED],
        RequirementState.COMPLETED: [RequirementState.DESIGN]
    }

    TECHNICAL_TRANSITIONS = {
        RequirementState.NEW: [RequirementState.ANALYSIS],
        RequirementState.ANALYSIS: [RequirementState.DESIGN, RequirementState.NEW],
        RequirementState.DESIGN: [RequirementState.ANALYSIS, RequirementState.DEVELOPMENT],
        RequirementState.DEVELOPMENT: [RequirementState.DESIGN, RequirementState.TESTING],
        RequirementState.TESTING: [RequirementState.DEVELOPMENT, RequirementState.COMPLETED],
        RequirementState.COMPLETED: [RequirementState.TESTING]
    }

    # New simplified 4-state workflow transitions
    SIMPLIFIED_TRANSITIONS = {
        RequirementState.BACKLOG: [RequirementState.TODO],
        RequirementState.TODO: [RequirementState.BACKLOG, RequirementState.IN_REVIEW],
        RequirementState.IN_REVIEW: [RequirementState.TODO, RequirementState.DONE],
        RequirementState.DONE: [RequirementState.IN_REVIEW]
    }

    # Mapping from old states to new states
    OLD_TO_NEW_STATE_MAP = {
        RequirementState.NEW: RequirementState.BACKLOG,
        RequirementState.ANALYSIS: RequirementState.TODO,
        RequirementState.DESIGN: RequirementState.TODO,
        RequirementState.DEVELOPMENT: RequirementState.IN_REVIEW,
        RequirementState.TESTING: RequirementState.IN_REVIEW,
        RequirementState.COMPLETED: RequirementState.DONE
    }

    @staticmethod
    def can_transition(from_state, to_state, project_type):
        """Check if a transition between states is valid."""
        # Check if using simplified states
        if from_state in RequirementStateMachine.SIMPLIFIED_TRANSITIONS:
            return to_state in RequirementStateMachine.SIMPLIFIED_TRANSITIONS.get(from_state, [])

        # Original transition logic for backward compatibility
        transitions = (
            RequirementStateMachine.TECHNICAL_TRANSITIONS
            if project_type == "technical"
            else RequirementStateMachine.NON_TECHNICAL_TRANSITIONS
        )
        return to_state in transitions.get(from_state, [])

    @staticmethod
    def is_backward_transition(from_state, to_state, project_type):
        """Check if a transition is backward (returns to previous state)."""
        # Check simplified states first
        if (from_state in RequirementStateMachine.SIMPLIFIED_TRANSITIONS and
            to_state in RequirementStateMachine.SIMPLIFIED_TRANSITIONS):
            state_order = [
                RequirementState.BACKLOG, RequirementState.TODO,
                RequirementState.IN_REVIEW, RequirementState.DONE
            ]
            try:
                return state_order.index(to_state) < state_order.index(from_state)
            except ValueError:
                return False

        # Original logic for backward compatibility
        transitions = (
            RequirementStateMachine.TECHNICAL_TRANSITIONS
            if project_type == "technical"
            else RequirementStateMachine.NON_TECHNICAL_TRANSITIONS
        )
        state_order = [
            RequirementState.NEW, RequirementState.ANALYSIS, RequirementState.DESIGN,
            RequirementState.DEVELOPMENT, RequirementState.TESTING, RequirementState.COMPLETED
        ]
        try:
            return state_order.index(to_state) < state_order.index(from_state)
        except ValueError:
            return False

    @staticmethod
    def get_new_state(old_state):
        """Map old state to new simplified state."""
        return RequirementStateMachine.OLD_TO_NEW_STATE_MAP.get(old_state, old_state)
