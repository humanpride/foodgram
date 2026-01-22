// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

process.on('unhandledRejection', (reason) => {
//   if (
//     reason instanceof TypeError &&
//     reason.message.includes('Failed to parse URL')
//   ) {
//     return;
//   }
//   console.error('Unhandled Rejection in test:', reason);
    return;
});
