import { useTeamStore } from '@/app/stores/teamStore';

export function useAIAgents() {
  const { aiAgents, addAgent, updateAgent, removeAgent, getAgentByRole } = useTeamStore();

  const getAnalysisAgent = () => getAgentByRole('analysis_agent');
  const getDesignAgent = () => getAgentByRole('design_agent');
  const getDevelopmentAgent = () => getAgentByRole('development_agent');
  const getTestingAgent = () => getAgentByRole('testing_agent');

  return {
    agents: aiAgents,
    addAgent,
    updateAgent,
    removeAgent,
    getAgentByRole,
    getAnalysisAgent,
    getDesignAgent,
    getDevelopmentAgent,
    getTestingAgent
  };
}
