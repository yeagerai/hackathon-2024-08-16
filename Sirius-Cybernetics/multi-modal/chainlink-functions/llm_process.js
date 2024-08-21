// llm_processor.js

const prompt = args[0];
const transformationType = args[1];
const selectedLLM = args[2];
const imageData = args[3];

// Define LLM endpoints and models
const llmEndpoints = {
    "chatgpt-3-turbo": {
        url: "https://api.openai.com/v1/chat/completions",
        model: "gpt-3.5-turbo",
        method: "POST",
        headers: {
            'Authorization': `Bearer ${secrets.openaiKey}`,
            'Content-Type': 'application/json'
        },
        data: (prompt) => ({ model: "gpt-3.5-turbo", messages: [{ role: "user", content: prompt }], temperature: 0.7 })
    },
    "text-davinci-003": {
        url: "https://api.openai.com/v1/completions",
        model: "text-davinci-003",
        method: "POST",
        headers: {
            'Authorization': `Bearer ${secrets.openaiKey}`,
            'Content-Type': 'application/json'
        },
        data: (prompt) => ({ model: "text-davinci-003", prompt: prompt, temperature: 0, max_tokens: 150 })
    },
    // Add more LLMs as needed
};

// Define prompts based on transformation types
const prompts = {
    "resize": `Resize the following image to the specified dimensions.

Image Data: ${imageData}
Transformation: Resize
Dimensions: [WIDTH]x[HEIGHT]`,
    
    "crop": `Crop the following image to the specified area.

Image Data: ${imageData}
Transformation: Crop
Coordinates: [X],[Y],[WIDTH],[HEIGHT]`,
    
    "color_adjustment": `Adjust the colors of the following image.

Image Data: ${imageData}
Transformation: Color Adjustment
Parameters: [BRIGHTNESS],[CONTRAST],[SATURATION]`,
    
    "rotate": `Rotate the following image by the specified angle.

Image Data: ${imageData}
Transformation: Rotate
Angle: [ANGLE] degrees`,
    
    "filter": `Apply the specified filter to the following image.

Image Data: ${imageData}
Transformation: Filter
Filter Type: [FILTER_TYPE]`,
};

// Check if the selected LLM is valid
if (!llmEndpoints[selectedLLM]) {
    throw Error("Invalid LLM selected");
}

// Check if the transformation type has a corresponding prompt
if (!prompts[transformationType]) {
    throw Error("Invalid transformation type");
}

const llm = llmEndpoints[selectedLLM];
const promptText = prompts[transformationType].replace("[WIDTH]", "100").replace("[HEIGHT]", "100"); // Replace placeholders as needed

// Make the HTTP request to the selected LLM
const llmRequest = Functions.makeHttpRequest({
    url: llm.url,
    method: llm.method,
    headers: llm.headers,
    data: llm.data(promptText)
});

const [llmResponse] = await Promise.all([llmRequest]);
console.log("raw response", llmResponse);

const result = llmResponse.data.choices ? llmResponse.data.choices[0].text : llmResponse.data.choices[0].message.content;
return Functions.encodeString(result);
