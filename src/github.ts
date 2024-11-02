import axios from "axios";

const GITHUB_API_URL =
  "https://api.github.com/repos/manudelp/ultimate-tic-tac-toe/commits";

export const getLatestCommitHash = async () => {
  const token = process.env.NEXT_PUBLIC_GITHUB_TOKEN;

  try {
    const response = await axios.get(GITHUB_API_URL, {
      headers: {
        Authorization: `token ${token}`,
      },
    });

    const lastCommit = response.data[0]; // Get the most recent commit
    return lastCommit.sha; // Return the full commit hash
  } catch (error) {
    console.error("Error fetching last commit:", error);
    throw new Error("Failed to fetch last commit");
  }
};
