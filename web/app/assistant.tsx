"use client";

import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useRemoteThreadListRuntime } from "@assistant-ui/react";
import { useLangGraphRuntime } from "@assistant-ui/react-langgraph";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";

import { getThreadState, sendMessage } from "@/lib/chatApi";
import { langGraphAdapter } from "@/lib/langGraphAdapter";
import { Thread } from "@/components/assistant-ui/thread";
import { ThreadListSidebar } from "@/components/assistant-ui/threadlist-sidebar";

export function Assistant() {
  const runtime = useRemoteThreadListRuntime({
    runtimeHook: () =>
      useLangGraphRuntime({
        stream: async function* (messages, { initialize, command }) {
          const { externalId } = await initialize();
          if (!externalId) throw new Error("Thread not found");

          const generator = await sendMessage({
            threadId: externalId,
            messages,
            command,
          });

          yield* generator;
        },
        load: async (externalId) => {
          const state = await getThreadState(externalId);
          return {
            messages: state.values.messages ?? [],
          };
        },
      }),
    adapter: langGraphAdapter,
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <SidebarProvider>
        <ThreadListSidebar />
        <SidebarInset>
          <Thread />
        </SidebarInset>
      </SidebarProvider>
    </AssistantRuntimeProvider>
  );
}
