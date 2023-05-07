/*
An average-load test assesses how the system performs under typical load.
Typical load might be a regular day in production or an average moment.

Average-load tests simulate the number of concurrent users and requests per second
that reflect average behaviors in the production environment.
This type of test typically increases the throughput or VUs gradually
and keeps that average load for some time. Depending on the system's characteristics,
the test may stop suddenly or have a short ramp-down period.
*/

import http from "k6/http";
import { check, sleep } from "k6";

// read t8.shakespeare.txt
const file = open('./t8.shakespeare.txt');

// 1. start docker
// 2. terminal 1: docker-compose up
// 3. terminal 2: cd examples
// 4. terminal 2: source env/bin/activate
// 5. terminal 2: python3 main.py
// 6. terminal 3: brew install k6
// 7. terminal 3: k6 run k6/average_load_test.js

/*
     checks.........................: 50.87% ✓ 3005     ✗ 2902 
     data_received..................: 67 MB  28 kB/s
     data_sent......................: 1.3 MB 543 B/s
     http_req_blocked...............: avg=264.34ms min=0s      med=4µs    max=19.5s  p(90)=1.58ms p(95)=1.92ms
     http_req_connecting............: avg=264.32ms min=0s      med=0s     max=19.5s  p(90)=1.55ms p(95)=1.9ms 
     http_req_duration..............: avg=35.33s   min=68µs    med=47.07s max=1m0s   p(90)=1m0s   p(95)=1m0s  
       { expected_response:true }...: avg=19.64s   min=14.22ms med=11.35s max=59.89s p(90)=51.4s  p(95)=55.59s
     http_req_failed................: 49.12% ✓ 2902     ✗ 3005 
     http_req_receiving.............: avg=18.45µs  min=0s      med=11µs   max=448µs  p(90)=52µs   p(95)=63µs  
     http_req_sending...............: avg=10.69µs  min=2µs     med=8µs    max=231µs  p(90)=19µs   p(95)=27µs  
     http_req_tls_handshaking.......: avg=0s       min=0s      med=0s     max=0s     p(90)=0s     p(95)=0s    
     http_req_waiting...............: avg=35.33s   min=48µs    med=47.07s max=1m0s   p(90)=1m0s   p(95)=1m0s  
     http_reqs......................: 5907   2.447446/s
     iteration_duration.............: avg=1m10s    min=1.19ms  med=1m21s  max=2m0s   p(90)=2m0s   p(95)=2m0s  
     iterations.....................: 2929   1.213572/s
     vus............................: 6      min=1      max=100
     vus_max........................: 100    min=100    max=100


running (40m13.5s), 000/100 VUs, 2929 complete and 74 interrupted iterations
default ✓ [======================================] 000/100 VUs  40m0s
*/

// TODO: currently running on the example which is not optimally configured for prod, rasther a dev instance

// Test configuration
export const options = {
  // Key configurations for avg load test in this section
  stages: [
    { duration: '5m', target: 100 }, // traffic ramp-up from 1 to 100 users over 5 minutes.
    { duration: '30m', target: 100 }, // stay at 100 users for 10 minutes
    { duration: '5m', target: 0 }, // ramp-down to 0 users
  ],
};



export default function () {
  // pick a random chunk of length 50 from the file
  const index = Math.floor(Math.random() * file.length)
  const chunk = file.substring(index, index + 50)
  const payload = JSON.stringify({
    documents: [{
      data: chunk,
    }],
  });
  const headers = { 'Content-Type': 'application/json' };
  const res = http.post('http://localhost:8000/v1/load-test', payload, {
    headers,
  });

  // console.log(`Payload: ${payload}`);

  check(res, {
    'Post status is 200': (r) => res.status === 200,
  });

  const searchPayload = JSON.stringify({ query: chunk });
  const searchRes = http.post('http://localhost:8000/v1/load-test/search', searchPayload, { headers });

  check(searchRes, {
    'Search status is 200': (r) => searchRes.status === 200,
  });

  // sleep(1);
}