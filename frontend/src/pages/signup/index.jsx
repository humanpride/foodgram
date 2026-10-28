import {
  Container,
  Input,
  FormTitle,
  Main,
  Form,
  Button,
} from "../../components";
import styles from "./styles.module.css";
import { useFormWithValidation } from "../../utils";
import { Navigate } from "react-router-dom";
import { useContext } from "react";
import { AuthContext } from "../../contexts";
import { Helmet } from "react-helmet-async";

const SignUp = ({ onSignUp, submitError, setSubmitError }) => {
  const { values, handleChange, errors } = useFormWithValidation();
  const authContext = useContext(AuthContext);

  const onChange = (e) => {
    setSubmitError({ submitError: "" });
    handleChange(e);
  };

  return (
    <Main withBG asFlex>
      {authContext && <Navigate to="/recipes" />}
      <Container className={styles.center}>
        <Helmet>
          <title>Sign Up</title>
          <meta
            name="description"
            content="Foodgram - Sign Up"
          />
          <meta property="og:title" content="Sign Up" />
        </Helmet>
        <Form
          className={styles.form}
          onSubmit={(e) => {
            e.preventDefault();
            onSignUp(values);
          }}
        >
          <FormTitle>Sign Up</FormTitle>
          <Input
            placeholder="First Name"
            name="first_name"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />
          <Input
            placeholder="Last Name"
            name="last_name"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />
          <Input
            placeholder="Username"
            name="username"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />

          <Input
            placeholder="Email address"
            name="email"
            required
            isAuth={true}
            error={errors}
            onChange={onChange}
          />
          <Input
            placeholder="Password"
            type="password"
            name="password"
            required
            isAuth={true}
            error={errors}
            submitError={submitError}
            onChange={onChange}
          />
          <Button modifier="style_dark" type="submit" className={styles.button}>
            Create account
          </Button>
        </Form>
      </Container>
    </Main>
  );
};

export default SignUp;
