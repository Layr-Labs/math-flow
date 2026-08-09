import researchData from "./math-flow-data.json";
import { KnowledgeViewer } from "./KnowledgeViewer";

export default function Home() {
  return <KnowledgeViewer data={researchData} />;
}
