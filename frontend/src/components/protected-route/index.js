import React from 'react';
import { Route, Navigate } from "react-router-dom";

function ProtectedRoute({ exact, component: Component, path, ...props }) {
  return (
    <Route path={path} exact={exact}>
      {
        () => props.loggedIn ? <Component {...props} /> : <Navigate to='/recipes' />
      } 
    </Route>
  )
}
export default ProtectedRoute;