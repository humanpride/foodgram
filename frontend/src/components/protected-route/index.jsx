import React from "react";
import { Navigate, useLocation } from "react-router-dom";

/**
 * Protected route.
 *
 * Usage (recommended, as in your App.js):
 * <Route path="/cart" element={
 *   <ProtectedRoute isAuth={loggedIn}>
 *     <Cart />
 *   </ProtectedRoute>
 * } />
 *
 * Alternatively (legacy style, for compatibility):
 * <ProtectedRoute component={Cart} isAuth={loggedIn} />
 *
 * props:
 *  - isAuth (boolean) or loggedIn (boolean) — whether the user is authenticated
 *  - redirectTo (string) — redirect destination for unauthenticated users (defaults to "/signin")
 *  - children — child component(s) to display when authenticated
 *  - component — (optional) component to render (for compatibility with legacy code)
 */
function ProtectedRoute({
  isAuth,
  loggedIn, // support the legacy prop name
  redirectTo = "/signin",
  children,
  component: Component,
  ...rest
}) {
  const auth = typeof isAuth !== "undefined" ? isAuth : loggedIn;
  const location = useLocation();

  if (auth) {
    // if component is provided (legacy style), render it
    if (Component) {
      return <Component {...rest} />;
    }
    // otherwise, render children (recommended)
    return children;
  }

  // if unauthenticated, redirect to the sign-in page and preserve the original location
  return <Navigate to={redirectTo} replace state={{ from: location }} />;
}

export default ProtectedRoute;
