import { Button, Container, Main } from "../../components";
import styles from "./styles.module.css";
import image from "../../images/not-found.png";
import { useNavigate } from 'react-router-dom';

const Favorites = () => {
  const navigate = useNavigate();

  const handleClick = () => navigate("/recipes", { replace: true });

  return (
    <Main className={styles.root}>
      <Container>
        <img src={image} className={styles.img} alt="логотип." />
        <p className={styles.text}>Page not found</p>
        <Button
          modifier="style_dark"
          className={styles.button}
          onClick={handleClick}
        >
          Home page
        </Button>
      </Container>
    </Main>
  );
};

export default Favorites;
