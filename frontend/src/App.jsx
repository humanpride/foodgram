import "./fonts/SanFranciscoProDisplay/fonts.css";
import "./App.css";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import React, { useState, useEffect } from "react";
import { Header, Footer, ProtectedRoute } from "./components";
import api from "./api";
import styles from "./styles.module.css";

import {
  Main,
  Cart,
  SignIn,
  Subscriptions,
  Favorites,
  SingleCard,
  SignUp,
  RecipeEdit,
  RecipeCreate,
  User,
  ChangePassword,
  NotFound,
  UpdateAvatar,
  ResetPassword,
} from "./pages";

import { AuthContext, UserContext } from "./contexts";

function App() {
  const [loggedIn, setLoggedIn] = useState(null);
  const [user, setUser] = useState({});
  const [orders, setOrders] = useState(0);
  const [authError, setAuthError] = useState({ submitError: "" });
  const [registrError, setRegistrError] = useState({ submitError: "" });
  const [changePasswordError, setChangePasswordError] = useState({
    submitError: "",
  });

  const navigate = useNavigate();

  const registration = ({ email, password, username, first_name, last_name }) => {
    api
      .signup({ email, password, username, first_name, last_name })
      .then(() => {
        navigate("/signin");
      })
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) setRegistrError({ submitError: errors.join(", ") });
        setLoggedIn(false);
      });
  };

  const authorization = ({ email, password }) => {
    api
      .signin({ email, password })
      .then((res) => {
        if (res.auth_token) {
          localStorage.setItem("token", res.auth_token);
          api
            .getUserData()
            .then((res) => {
              setUser(res);
              setLoggedIn(true);
              getOrders();
            })
            .catch(() => {
              setLoggedIn(false);
              navigate("/signin");
            });
        } else {
          setLoggedIn(false);
        }
      })
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) setAuthError({ submitError: errors.join(", ") });
        setLoggedIn(false);
      });
  };

  const changePassword = ({ new_password, current_password }) => {
    api
      .changePassword({ new_password, current_password })
      .then(() => navigate("/signin"))
      .catch((err) => {
        const errors = Object.values(err);
        if (errors) setChangePasswordError({ submitError: errors.join(", ") });
      });
  };

  const changeAvatar = ({ file }) => {
    api
      .changeAvatar({ file })
      .then((res) => {
        setUser({ ...user, avatar: res.avatar });
        navigate("/recipes");
      })
      .catch((err) => {
        const errors = Object.values(err);
        alert(errors.join(", "));
      });
  };

  const onPasswordReset = ({ email }) => {
    api
      .resetPassword({ email })
      .then(() => navigate("/signin"))
      .catch((err) => {
        const errors = Object.values(err);
        alert(errors.join(", "));
        setLoggedIn(false);
      });
  };

  const onSignOut = () => {
    api
      .signout()
      .then(() => {
        localStorage.removeItem("token");
        setLoggedIn(false);
      })
      .catch((err) => {
        const errors = Object.values(err);
        alert(errors.join(", "));
      });
  };

  const getOrders = () => {
    api
      .getRecipes({ page: 1, is_in_shopping_cart: Number(true) })
      .then((res) => setOrders(res.count));
  };

  const updateOrders = (add) => {
    if (!add && orders <= 0) return;
    setOrders((prev) => (add ? prev + 1 : prev - 1));
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api
        .getUserData()
        .then((res) => {
          setUser(res);
          setLoggedIn(true);
          getOrders();
        })
        .catch(() => {
          setLoggedIn(false);
          navigate("/recipes");
        });
    } else {
      setLoggedIn(false);
    }
  }, []);

  if (loggedIn === null) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <AuthContext.Provider value={loggedIn}>
      <UserContext.Provider value={user}>
        <div className="App">
          <Header orders={orders} loggedIn={loggedIn} onSignOut={onSignOut} />
          <Routes>
            <Route
              path="/user/:id"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <User updateOrders={updateOrders} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/cart"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <Cart orders={orders} updateOrders={updateOrders} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/subscriptions"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <Subscriptions />
                </ProtectedRoute>
              }
            />

            <Route
              path="/favorites"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <Favorites updateOrders={updateOrders} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/recipes/create"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <RecipeCreate />
                </ProtectedRoute>
              }
            />

            <Route
              path="/recipes/:id/edit"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <RecipeEdit loadItem={() => {}} onItemDelete={getOrders} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/change-password"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <ChangePassword
                    submitError={changePasswordError}
                    setSubmitError={setChangePasswordError}
                    onPasswordChange={changePassword}
                  />
                </ProtectedRoute>
              }
            />

            <Route
              path="/change-avatar"
              element={
                <ProtectedRoute isAuth={loggedIn}>
                  <UpdateAvatar onAvatarChange={changeAvatar} />
                </ProtectedRoute>
              }
            />

            <Route
              path="/recipes/:id"
              element={<SingleCard updateOrders={updateOrders} />}
            />

            <Route path="/reset-password" element={<ResetPassword onPasswordReset={onPasswordReset} />} />
            <Route path="/recipes" element={<Main updateOrders={updateOrders} />} />
            <Route
              path="/signin"
              element={<SignIn onSignIn={authorization} submitError={authError} setSubmitError={setAuthError} />}
            />
            <Route
              path="/signup"
              element={<SignUp onSignUp={registration} submitError={registrError} setSubmitError={setRegistrError} />}
            />
            <Route path="/" element={<Navigate to="/recipes" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <Footer />
        </div>
      </UserContext.Provider>
    </AuthContext.Provider>
  );
}

export default App;
