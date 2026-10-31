import React from 'react'
import PropTypes from 'prop-types'
import styles from './styles.module.css'
import { Subscription } from '../index'

const SubscriptionList = ({ subscriptions = [], removeSubscription }) => {
  // defensive check: if the value is not an array, assume there are no subscriptions
  if (!Array.isArray(subscriptions) || subscriptions.length === 0) {
    return (
      <div className={styles.subscriptionList}>
        {/* Replace with any UI: a spinner, an empty state, or a link */}
        <p>You are not following anyone yet.</p>
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
