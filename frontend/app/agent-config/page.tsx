import { getAgentConfig, getEnrichmentStatus } from "@/lib/api";
import { ConfigureAgentForm } from "./configure-agent-form";

export default async function AgentConfigPage() {
  const [config, status] = await Promise.all([
    getAgentConfig(),
    getEnrichmentStatus(),
  ]);

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
      <div className="space-y-1">
        <h1 className="font-heading text-xl font-semibold tracking-normal sm:text-2xl">
          Configure Agent
        </h1>
        <p className="text-sm text-muted-foreground">
          Control how the AI enriches new timeline posts. Changes take effect on
          the next enrichment run.
        </p>
      </div>

      <ConfigureAgentForm initialConfig={config} initialStatus={status} />
    </main>
  );
}
