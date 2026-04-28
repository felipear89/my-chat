import { Client, ThreadState } from "@langchain/langgraph-sdk";
import {
  LangChainMessage,
  LangGraphCommand,
} from "@assistant-ui/react-langgraph";

const createClient = () => {
  const apiUrl =
    process.env["NEXT_PUBLIC_LANGGRAPH_API_URL"] ||
    new URL("/api", window.location.href).href;
  return new Client({
    apiUrl,
  });
};

export const getUserId = (): string => {
  const key = "chat_user_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
};

export const createThread = async () => {
  const client = createClient();
  return client.threads.create({ metadata: { userId: getUserId() } });
};

export const getThreadState = async (
  threadId: string,
): Promise<ThreadState<{ messages: LangChainMessage[] }>> => {
  const client = createClient();
  return client.threads.getState(threadId);
};

export const listThreads = async () => {
  const client = createClient();
  return client.threads.search({ metadata: { userId: getUserId() }, limit: 100 });
};

export const fetchThread = async (threadId: string) => {
  const client = createClient();
  return client.threads.get(threadId);
};

export const deleteThread = async (threadId: string) => {
  const client = createClient();
  return client.threads.delete(threadId);
};

export const updateThreadTitle = async (threadId: string, title: string) => {
  const client = createClient();
  return client.threads.update(threadId, { metadata: { title } });
};

export const sendMessage = async (params: {
  threadId: string;
  messages?: LangChainMessage[];
  command?: LangGraphCommand | undefined;
}) => {
  const client = createClient();
  return client.runs.stream(
    params.threadId,
    process.env["NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID"]!,
    {
      input: params.messages?.length
        ? {
            messages: params.messages,
          }
        : null,
      command: params.command,
      streamMode: ["messages", "updates", "custom"],
    },
  );
};
