import { createAssistantStream } from "assistant-stream";
import type { ThreadMessage } from "@assistant-ui/core";
import {
  createThread,
  deleteThread,
  fetchThread,
  listThreads,
  updateThreadTitle,
} from "./chatApi";

function getTitleFromMessages(messages: readonly ThreadMessage[]): string {
  const firstUser = messages.find((m) => m.role === "user");
  if (!firstUser) return "New Chat";
  const text = firstUser.content
    .filter((p): p is { type: "text"; text: string } => p.type === "text")
    .map((p) => p.text)
    .join("");
  return text.slice(0, 60) || "New Chat";
}

export const langGraphAdapter = {
  async list() {
    const threads = await listThreads();
    return {
      threads: threads.map((t) => ({
        status: "regular" as const,
        remoteId: t.thread_id,
        externalId: t.thread_id,
        title: (t.metadata as Record<string, unknown>)?.title as
          | string
          | undefined,
      })),
    };
  },

  async initialize(_threadId: string) {
    const { thread_id } = await createThread();
    return { remoteId: thread_id, externalId: thread_id };
  },

  async fetch(remoteId: string) {
    const t = await fetchThread(remoteId);
    return {
      status: "regular" as const,
      remoteId: t.thread_id,
      externalId: t.thread_id,
      title: (t.metadata as Record<string, unknown>)?.title as
        | string
        | undefined,
    };
  },

  async rename(remoteId: string, newTitle: string) {
    await updateThreadTitle(remoteId, newTitle);
  },

  async archive(_remoteId: string) {
    // LangGraph has no archive concept — no-op
  },

  async unarchive(_remoteId: string) {
    // LangGraph has no archive concept — no-op
  },

  async delete(remoteId: string) {
    await deleteThread(remoteId);
  },

  async generateTitle(
    remoteId: string,
    messages: readonly ThreadMessage[],
  ) {
    const title = getTitleFromMessages(messages);
    await updateThreadTitle(remoteId, title);
    return createAssistantStream((controller) => {
      controller.appendText(title);
      controller.close();
    });
  },
};
