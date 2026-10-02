import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import { Helmet } from 'react-helmet-async'

const About = ({ updateOrders, orders }) => {

  return <Main>
    <Helmet>
      <title>О проекте</title>
      <meta name="description" content="Foodgram - О проекте" />
      <meta property="og:title" content="О проекте" />
    </Helmet>

    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>О проекте</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для
              приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.
            </p>
            <p className={styles.textItem}>
              Чтобы использовать все возможности сайта — нужна регистрация. Проверка адреса электронной почты не осуществляется, вы можете ввести любой email.
            </p>
            <p className={styles.textItem}>
              Заходите и делитесь своими любимыми рецептами!
            </p>
          </div>
        </div>
      </div>

    </Container>
  </Main>
}

export default About
