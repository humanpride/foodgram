import styles from './styles.module.css'
import { useContext } from 'react'
import { LinkComponent, Account, Button } from '../index.js'
import { AuthContext } from '../../contexts'
import { useLocation } from 'react-router-dom'
import { NotLoggedInMenu } from '../../configs/navigation'

const AccountMenu = ({ onSignOut, orders }) => {
  const authContext = useContext(AuthContext)
  const location = useLocation()

  if (!authContext) {
    return (
      <div className={styles.menu}>
        {NotLoggedInMenu.map((item, index) => {
          const isActive = location.pathname === item.href
          if (isActive) {
            return (
              <Button
                key={item.href || index} // добавлен key
                href={item.href}
                modifier='style_dark'
                className={styles.menuButton}
              >
                {item.title}
              </Button>
            )
          } else {
            return (
              <LinkComponent
                key={item.href || index} // добавлен key
                title={item.title}
                href={item.href}
                className={styles.menuLink}
              />
            )
          }
        })}
      </div>
    )
  }

  return (
    <div className={styles.menu}>
      <Account onSignOut={onSignOut} orders={orders} />
    </div>
  )
}

export default AccountMenu
