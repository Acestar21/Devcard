import styles from './page.module.css';

export default function HomePage() {
  return (
    <main className={styles.container}>
      <h1 className={styles.heading}>DevCard</h1>
      <p className={styles.subtitle}>
        The identity layer for developers. Aggregate your GitHub activity in one place.
      </p>
      <a href={process.env.NEXT_PUBLIC_API_URL + '/auth/github/login'} className={styles.loginButton}>
        Log in with GitHub
      </a>
    </main>
  );
}
