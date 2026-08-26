import { mockOk } from "@/services/mock"
import {
  resolveResponse,
  type AIQueryContext,
  type AIResponseData,
} from "@/lib/ask-ai-data"

/** Future: POST /api/ai/query — question → intent detection → controlled
 *  Python data services → compact structured context → AIProvider. The
 *  frontend only renders the structured result. */
export function askAI(
  question: string,
  context?: AIQueryContext
): Promise<AIResponseData> {
  return mockOk(resolveResponse(question, context), 900)
}
