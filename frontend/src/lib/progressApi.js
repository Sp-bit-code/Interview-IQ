const SPRING_API_URL =
  (import.meta.env.VITE_PROGRESS_API_URL || "http://localhost:8081").replace(
    /\/$/,
    ""
  );

/**
 * Get all study progress for a user
 *
 * GET /api/progress/{userId}
 */
export async function getUserProgress(userId) {
  const response = await fetch(
    `${SPRING_API_URL}/api/progress/${encodeURIComponent(userId)}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch study progress");
  }

  return response.json();
}


/**
 * Add a new topic or update an existing topic
 *
 * POST /api/progress
 *
 * Example:
 * saveProgress({
 *   userId: "123",
 *   topicName: "Spring Dependency Injection",
 *   completed: true
 * });
 */
export async function saveProgress({
  userId,
  topicName,
  completed
}) {
  const response = await fetch(
    `${SPRING_API_URL}/api/progress`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        userId,
        topicName,
        completed
      })
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      errorText || "Failed to save study progress"
    );
  }

  return response.json();
}


/**
 * Get number of completed topics
 *
 * GET /api/progress/{userId}/completed-count
 */
export async function getCompletedTopicCount(userId) {
  const response = await fetch(
    `${SPRING_API_URL}/api/progress/${encodeURIComponent(
      userId
    )}/completed-count`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch completed topic count");
  }

  const data = await response.json();

  return data.completedTopics;
}


/**
 * Delete a progress record
 *
 * DELETE /api/progress/{id}
 */
export async function deleteProgress(id) {
  const response = await fetch(
    `${SPRING_API_URL}/api/progress/${encodeURIComponent(id)}`,
    {
      method: "DELETE"
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete study progress");
  }

  return response.json();
}