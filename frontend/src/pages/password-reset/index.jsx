import {
  Container,
  Input,
  Main,
  Form,
  Button,
  FormTitle
} from '../../components';
import styles from './styles.module.css';
import { useFormWithValidation } from '../../utils';
import { Helmet } from 'react-helmet-async';
import { AuthContext } from '../../contexts';
import { useContext } from 'react';
import { Navigate } from 'react-router-dom';

const ResetPassword = ({ onPasswordReset }) => {
  const { values, handleChange, isValid } = useFormWithValidation();
  const authContext = useContext(AuthContext);

  if (authContext) {
    return <Navigate to="/recipes" />;
  }

  return (
    <Main withBG asFlex>
      <Container className={styles.center}>
        <Helmet>
          <title>Reset password</title>
          <meta name="description" content="Foodgram - Reset password" />
          <meta property="og:title" content="Reset password" />
        </Helmet>

        <Form
          className={styles.form}
          onSubmit={e => {
            e.preventDefault();
            onPasswordReset(values);
          }}
        >
          <FormTitle>Reset password</FormTitle>

          <Input
            required
            name="email"
            placeholder="Email"
            onChange={handleChange}
          />

          <Button
            modifier="style_dark"
            disabled={!isValid}
            type="submit"
            className={styles.button}
          >
            Reset
          </Button>
        </Form>
      </Container>
    </Main>
  );
};

export default ResetPassword;
