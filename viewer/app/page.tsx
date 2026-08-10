import researchData from "./math-flow-data.json";
import { RepositoryKnowledgeViewer } from "./KnowledgeViewer";

export default function Home() {
  return <RepositoryKnowledgeViewer fallbackData={researchData} />;
}
