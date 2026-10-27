import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import { Helmet } from 'react-helmet-async'

const About = ({ updateOrders, orders }) => {

  return <Main>
    <Helmet>
      <title>About</title>
      <meta name="description" content="Foodgram - About" />
      <meta property="og:title" content="About" />
    </Helmet>

    <Container>
      <h1 className={styles.title}>Hello!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>About</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              This site lets users create and store recipes online. You can also download a list of ingredients needed to
              prepare a dish, browse friends' recipes, and save your favorite recipes.
            </p>
            <p className={styles.textItem}>
              Register to access all the site's features. Email addresses are not verified, so you can enter any email address.
            </p>
            <p className={styles.textItem}>
              Join us and share your favorite recipes!
            </p>
          </div>
        </div>
      </div>

    </Container>
  </Main>
}

export default About
