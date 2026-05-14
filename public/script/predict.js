const canvas = document.getElementById('prediction');
const ctx = canvas.getContext('2d');
const pyPort = 3000;
canvas.width = 280;
canvas.height = 280;

ctx.fillStyle = "black";
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.strokeStyle = "white";
ctx.lineWidth = 25;
ctx.lineCap = "round";
ctx.lineJoin = "round";

let isDrawing = false;

const draw = (event) => {
    if (!isDrawing) return;

    if (event.cancelable) event.preventDefault();

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const clientX = event.touches ? event.touches[0].clientX : event.clientX;
    const clientY = event.touches ? event.touches[0].clientY : event.clientY;

    const x = (clientX - rect.left) * scaleX;
    const y = (clientY - rect.top) * scaleY;

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

//Touch
canvas.addEventListener('touchstart', () => {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches[0].clientX;
    const clientY = e.touches[0].clientY;

    ctx.beginPath();
    ctx.moveTo(
        (clientX - rect.left) * (canvas.width / rect.width),
        (clientY - rect.top) * (canvas.height / rect.height)
    );
});
canvas.addEventListener('touchend', async () => {
    isDrawing = false;
    ctx.beginPath();
});

canvas.addEventListener('touchmove', draw);

canvas.addEventListener('resize', () => ctx.fillRect(0, 0, canvas.width, canvas.height));

const clearCanvas = () => {
    console.log("Pulito")
    ctx.fillRect(0, 0, canvas.width, canvas.height);
};

const canvasToBlob = async (canvas) => {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/png');
    });
};

const sendData = async () => {
    const blob = await canvasToBlob(canvas);
    const formData = new FormData();
    formData.append('file', blob, 'digit.png');

    try {
        const response = await fetch('/python/prediction', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        console.log("Previsione:", data.prediction);
        return data.prediction;

    } catch (error) {
        console.log("Errore durante la chiamata API:", error.message);
        alert(error.message)
    }
}
