let moment = require('moment')

export function formatDate () {
  return moment().startOf('day').fromNow()
}
