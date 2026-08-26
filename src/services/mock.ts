/*
 * Shared helpers for the mocked service layer. Every service function
 * returns a Promise so components/stores already consume the async shape
 * the future Django REST API will have — swapping these for fetch calls
 * must not require touching any component.
 */

export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function mockOk<T>(data: T, ms = 600): Promise<T> {
  await delay(ms)
  return data
}
