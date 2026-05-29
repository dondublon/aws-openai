const API_URL = "https://qrfd5s2xt9.execute-api.us-east-1.amazonaws.com/chat";
const INTERVAL_MS = 1000;

const payload = {
	query: "is there life on Mars",
};

async function sendQuery() {
	try {
		const response = await fetch(API_URL, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(payload),
		});

		console.log(response.status);
	} catch (error) {
		console.error( "request failed:", error.message);
	}
}

console.log(`Starting requests every ${INTERVAL_MS}ms to ${API_URL}`);

sendQuery();
const intervalId = setInterval(sendQuery, INTERVAL_MS);
setTimeout(()=>clearInterval(intervalId), 15 * 60 * 1000)

process.on("SIGINT", () => {
	clearInterval(intervalId);
	console.log("Stopped interval.");
    
})
