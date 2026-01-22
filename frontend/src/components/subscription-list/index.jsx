import React from 'react'
import PropTypes from 'prop-types'
import styles from './styles.module.css'
import { Subscription } from '../index'

const SubscriptionList = ({ subscriptions = [], removeSubscription }) => {
  // безопасная проверка: если передали не массив — считаем, что подписок нет
  if (!Array.isArray(subscriptions) || subscriptions.length === 0) {
    return (
      <div className={styles.subscriptionList}>
        {/* Можно заменить на любой UI — спиннер, пустое состояние или ссылку */}
        <p>У вас пока нет подписок.</p>
      </div>
    )
  }

  return (
    <div className={styles.subscriptionList}>
      {subscriptions.map(subscription => (
        <Subscription
          key={subscription.id}
          removeSubscription={removeSubscription}
          {...subscription}
        />
      ))}
    </div>
  )
}

SubscriptionList.propTypes = {
  subscriptions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    })
  ),
  removeSubscription: PropTypes.func,
}

SubscriptionList.defaultProps = {
  subscriptions: [],
  removeSubscription: () => {},
}

export default SubscriptionList
