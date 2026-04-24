const canvas = document.getElementById('prediction');
const ctx = canvas.getContext('2d');
const pyPort = 3000;
canvas.width = 280;
canvas.height = 280;

ctx.fillStyle = "black";
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = "white";
ctx.lineWidth = 20;
ctx.lineCap = "round";
ctx.lineJoin = "round";

let isDrawing = false;

const draw = (event)=> {
    if (!isDrawing) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

canvas.addEventListener('mousedown', () => isDrawing = true);
canvas.addEventListener('mouseup', async () => {
    isDrawing = false;
    ctx.beginPath();
});

canvas.addEventListener('mousemove', draw);
canvas.addEventListener('resize', () => ctx.fillRect(0, 0, canvas.width, canvas.height));

const clearCanvas = () => {
    console.log("Pulito")
    ctx.fillRect(0, 0, canvas.width, canvas.height);
};

const sendData = async () => {
    return canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'digit.png');

        try {
            console.log(window.location.origin)
            const response = await fetch(window.location.origin.replace(":8080", ":" + pyPort) + '/prediction', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            console.log("Previsione:", data.prediction);
            return data.predication;

        } catch (error) {
            console.error("Errore durante la chiamata API:", error);
            alert(error.message)
        }
    }, 'image/png');
}