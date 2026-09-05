import { notFound } from "next/navigation";
import { cookies } from "next/headers";
import Image from "next/image";
import { Profile } from "@/types";
import styles from "./page.module.css";

async function fetchProfile(
	username: string,
): Promise<{
	data: Profile | null;
	error: string | null;
	message: string | null;
}> {
	try {
		const cookieStore = await cookies();
		const sessionCookie = cookieStore.get("devcard_session");

		const res = await fetch(
			`${process.env.NEXT_PUBLIC_API_URL}/profiles/${username}`,
			{
				cache: "no-store",
				headers: sessionCookie
					? { Cookie: `devcard_session=${sessionCookie.value}` }
					: {},
			},
		);

		if (res.status === 404) {
			return { data: null, error: "NOT_FOUND", message: null };
		}

		if (!res.ok) {
			return {
				data: null,
				error: "FETCH_ERROR",
				message: `Server responded with ${res.status}: ${res.statusText}`,
			};
		}

		const data: Profile = await res.json();
    console.log('DEBUG deployed profile fetch:', data);
    
		return { data, error: null, message: null };
	} catch (e) {
		return {
			data: null,
			error: "NETWORK_ERROR",
			message:
				e instanceof Error
					? e.message
					: "A network error occurred while fetching the profile.",
		};
	}
}

export default async function ProfilePage({
	params,
}: {
	params: Promise<{ username: string }>;
}) {
	const { username } = await params;
	const { data: profile, error, message } = await fetchProfile(username);

	if (error === "NOT_FOUND") {
		notFound();
	}

	if (error) {
		return (
			<div className={styles.errorPage}>
				<p className={styles.errorMessage}>
					{message ||
						"An unexpected error occurred while loading the profile."}
				</p>
			</div>
		);
	}

	if (!profile) return null;

	return (
		<main className={styles.container}>
			<div className={styles.profileCard}>
				{/* Header */}
				<header className={styles.header}>
					<Image
						src={profile.avatar_url || ""}
						alt={profile.display_name || "Profile Picture"}
						width={96}
						height={96}
						className={styles.avatar}
					/>
					<div className={styles.nameContainer}>
						<h1 className={styles.displayName}>
							{profile.display_name || profile.username}
						</h1>
						<p className={styles.username}>@{profile.username}</p>
					</div>
				</header>

				{/* Bio */}
				{profile.bio && <p className={styles.bio}>{profile.bio}</p>}

				{/* GitHub Stats */}
				<section className={styles.section}>
					<h2 className={styles.sectionTitle}>GitHub Stats</h2>
					<div className={styles.statsGrid}>
						<div className={styles.statBlock}>
							<p className={styles.statLabel}>Contributions</p>
							<p className={styles.statValue}>
								{profile.stats.total_contributions}
							</p>
						</div>
						<div className={styles.statBlock}>
							<p className={styles.statLabel}>Top Languages</p>
							<div className={styles.langList}>
								{profile.stats.top_languages.map((lang) => (
									<span key={lang} className={styles.langTag}>
										{lang}
									</span>
								))}
							</div>
						</div>
						<div className={styles.statBlock}>
							<p className={styles.statLabel}>Pinned Repos</p>
							<p className={styles.statValue}>
								{profile.stats.pinned_repos.length}
							</p>
						</div>
					</div>

					<div className={styles.repoGrid}>
						{profile.stats.pinned_repos.map((repo) => (
							<a
								key={repo.name}
								href={repo.url}
								target="_blank"
								className={styles.repoCard}
							>
								<span className={styles.repoName}>
									{repo.name}
								</span>
								<p className={styles.repoDesc}>
									{repo.description ||
										"No description provided."}
								</p>
								<span className={styles.repoStars}>
									⭐ {repo.stars}
								</span>
							</a>
						))}
					</div>
				</section>
				{profile.is_owner && (
					<section className={styles.section}>
						<h2 className={styles.sectionTitle}>Your Badge</h2>
						<img
							src={`${process.env.NEXT_PUBLIC_API_URL}/badge/${profile.username}`}
							alt="DevCard badge"
							className={styles.badgePreview}
						/>
						<p className={styles.badgeInstructions}>
							Copy this into your README:
						</p>
						<code className={styles.badgeCode}>
							{`![DevCard](${process.env.NEXT_PUBLIC_API_URL}/badge/${profile.username})`}
						</code>
						<a
							href={`${process.env.NEXT_PUBLIC_API_URL}/auth/github/logout`}
							className={styles.logoutButton}
						>
							Log out
						</a>
					</section>
				)}
			</div>
		</main>
	);
}
