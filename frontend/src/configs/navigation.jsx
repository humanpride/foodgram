import Icons from "../components/icons"

export default [
  {
    title: 'Recipes',
    href: '/recipes',
    auth: false
  }, {
    title: 'Create a recipe',
    href: '/recipes/create',
    auth: true
  }
]

export const UserMenu = [
  {
    title: 'My subscriptions',
    href: '/subscriptions',
    auth: true,
    icon: <Icons.SubscriptionsMenu />
  }, {
    title: 'Favorites',
    href: '/favorites',
    auth: true,
    icon: <Icons.SavedMenu />
  }, {

    title: 'Change password',
    href: '/change-password',
    auth: true,
    icon: <Icons.ResetPasswordMenu />
  }
]

export const NotLoggedInMenu = [
  {
    title: 'Sign In',
    href: '/signin',
    auth: false
  }, {
    title: 'Sign Up',
    href: '/signup',
    auth: false
  }
]
