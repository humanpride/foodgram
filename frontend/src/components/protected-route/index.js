import React from "react";
import { Navigate, useLocation } from "react-router-dom";

/**
 * Защищённый маршрут.
 *
 * Использование (рекомендуемое — как у вас в App.js):
 * <Route path="/cart" element={
 *   <ProtectedRoute isAuth={loggedIn}>
 *     <Cart />
 *   </ProtectedRoute>
 * } />
 *
 * Альтернативно (устаревший стиль, для совместимости):
 * <ProtectedRoute component={Cart} isAuth={loggedIn} />
 *
 * props:
 *  - isAuth (boolean) или loggedIn (boolean) — флаг, авторизован ли пользователь
 *  - redirectTo (string) — куда редиректить при отсутствии авторизации (по умолчанию "/signin")
 *  - children — дочерний компонент(ы), которые нужно показать, если авторизован
 *  - component — (опционально) компонент для рендера (для совместимости со старым кодом)
 */
function ProtectedRoute({
  isAuth,
  loggedIn, // поддержка старого имени пропса
  redirectTo = "/signin",
  children,
  component: Component,
  ...rest
}) {
  const auth = typeof isAuth !== "undefined" ? isAuth : loggedIn;
  const location = useLocation();

  if (auth) {
    // если передан component (старый стиль) — отрендерим его
    if (Component) {
      return <Component {...rest} />;
    }
    // иначе — отрендерим children (рекомендуемый способ)
    return children;
  }

  // не авторизован — редирект на страницу входа, сохраним откуда пришли
  return <Navigate to={redirectTo} replace state={{ from: location }} />;
}

export default ProtectedRoute;
