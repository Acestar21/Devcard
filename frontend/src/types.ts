export interface SocialLink {
  platform: string;
  url: string;
}

export interface GitHubStats {
  total_contributions: number;
  top_languages: string[];
  pinned_repos: Array<{
    name: string;
    description: string | null;
    stars: number;
    url: string;
  }>;
}

export interface Profile {
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  theme: string;
  stats: GitHubStats;
  is_owner: boolean;
}
