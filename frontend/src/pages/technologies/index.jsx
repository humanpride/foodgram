import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import { Helmet } from 'react-helmet-async'

const Technologies = () => {
  return (
    <Main>
      <Helmet>
        <title>About</title>
        <meta name="description" content="Foodgram - Technologies" />
        <meta property="og:title" content="About" />
      </Helmet>

      <Container>
        <h1 className={styles.title}>Technologies</h1>
        <div className={styles.content}>
          <div>
            <h2 className={styles.subtitle}>
              Technologies used in this project:
            </h2>
            <div className={styles.text}>
              <ul className={styles.textItem}>
                <li className={styles.textItem}>Python</li>
                <li className={styles.textItem}>Django</li>
                <li className={styles.textItem}>Django REST Framework</li>
                <li className={styles.textItem}>Djoser</li>
              </ul>
            </div>
          </div>
        </div>
      </Container>
    </Main>
  )
}

export default Technologies
