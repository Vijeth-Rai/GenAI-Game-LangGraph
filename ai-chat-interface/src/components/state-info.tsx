// 'use client';

// import React, { useState, useEffect } from 'react';

// type StateInfo = {
//   current: string;
//   next: string;
// };

// export function StateInfoComponent() {
//   const [stateInfo, setStateInfo] = useState<StateInfo>({ current: '', next: '' });

//   useEffect(() => {
//     const eventSource = new EventSource('/api/python-script');
//     let messageCount = 0;


//     eventSource.onmessage = (event) => {
//       console.log('StateInfoComponent: Received message', event);
//       messageCount++;
//       const data = event.data.trim();

//       if (messageCount === 1) {
//         console.log('StateInfoComponent: Updating current state', data);
//         setStateInfo(prevState => ({ ...prevState, current: data }));
//       } else if (messageCount === 2) {
//         console.log('StateInfoComponent: Updating next state', data);
//         setStateInfo(prevState => ({ ...prevState, next: data }));
//         messageCount = 0; // Reset the count after processing the second message
//       }
//       // Ignore the third message
//     };

//     return () => {
//       eventSource.close();
//     };
//   }, []);

//   return (
//     <div className="state-info">
//       <h2>Current State: {stateInfo.current}</h2>
//       <h2>Next State: {stateInfo.next}</h2>
//     </div>
//   );
// }