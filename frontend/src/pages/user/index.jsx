import {
  Card,
  Title,
  Pagination,
  CardList,
  Button,
  CheckboxGroup,
  Container,
  Main,
  Icons,
} from "../../components";
import cn from "classnames";
import styles from "./styles.module.css";
import { useRecipes } from "../../utils/index.js";
import { useEffect, useState, useContext } from "react";
import api from "../../api";
import { useParams, useNavigate } from "react-router-dom";
import { AuthContext, UserContext } from "../../contexts";
import { Helmet } from "react-helmet-async";
import DefaultImage from "../../images/userpic-icon.jpg";

const UserPage = ({ updateOrders }) => {
  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    setTagsValue,
    handleTagsChange,
    handleLike,
    handleAddToCart,
  } = useRecipes();
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [subscribed, setSubscribed] = useState(false);
  const navigate = useNavigate();
  const userContext = useContext(UserContext);
  const authContext = useContext(AuthContext);

  const getRecipes = ({ page = 1, tags }) => {
    api.getRecipes({ page, author: id, tags }).then((res) => {
      setRecipes(res.results);
      setRecipesCount(res.count);
    });
  };

  const getUser = () => {
    api
      .getUser({ id })
      .then((res) => {
        setUser(res);
        setSubscribed(res.is_subscribed);
      })
      .catch(() => {
        navigate("/not-found");
      });
  };

  useEffect(() => {
    if (user) {
      getRecipes({ page: recipesPage, tags: tagsValue, author: user.id });
    }
  }, [recipesPage, tagsValue, user]);

  useEffect(() => {
    getUser();
  }, []);

  useEffect(() => {
    api.getTags().then((tags) => {
      setTagsValue(tags.map((tag) => ({ ...tag, value: true })));
    });
  }, []);

  const pageTitle = user ? `${user.first_name} ${user.last_name}` : "Страница пользователя";

  return (
    <Main>
      <Container className={styles.container}>
        <Helmet>
          <title>{pageTitle}</title>
          <meta name="description" content={`Фудграм - ${pageTitle}`} />
          <meta property="og:title" content={pageTitle} />
        </Helmet>

        <div className={styles.title}>
          <div className={styles.titleTextBox}>
            <div className={styles.user}>
              <div
                className={styles.userAvatar}
                style={{
                  backgroundImage: `url(${(user && user.avatar) || DefaultImage})`,
                }}
              />
              <Title className={styles.titleText} title={user ? pageTitle : ""} />
            </div>

            {(userContext?.id !== user?.id) && authContext && (
              <Button
                className={cn(styles.buttonSubscribe, { [styles.buttonSubscribeActive]: subscribed })}
                modifier={subscribed ? "style_dark" : "style_light"}
                clickHandler={() => {
                  const method = subscribed ? api.deleteSubscriptions.bind(api) : api.subscribe.bind(api);
                  method({ author_id: id }).then(() => setSubscribed(!subscribed));
                }}
              >
                <Icons.AddUser /> {subscribed ? "Отписаться от автора" : "Подписаться на автора"}
              </Button>
            )}
          </div>

          <CheckboxGroup
            values={tagsValue}
            handleChange={(value) => {
              setRecipesPage(1);
              handleTagsChange(value);
            }}
          />
        </div>

        {recipes.length > 0 && (
          <CardList>
            {recipes.map((card) => (
              <Card
                {...card}
                key={card.id}
                updateOrders={updateOrders}
                handleLike={handleLike}
                handleAddToCart={handleAddToCart}
              />
            ))}
          </CardList>
        )}

        <Pagination
          count={recipesCount}
          limit={6}
          page={recipesPage}
          onPageChange={(page) => setRecipesPage(page)}
        />
      </Container>
    </Main>
  );
};

export default UserPage;
