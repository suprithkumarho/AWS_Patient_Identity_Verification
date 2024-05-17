function uploadImage() {
    var fileInput = document.getElementById('imageUpload');
    var file = fileInput.files[0];
    var reader = new FileReader();

    reader.onload = function (e) {
        var base64data = e.target.result;
        document.getElementById('uploadedImage').src = base64data;
        document.getElementById('uploadedImage').style.display = 'block';

        var cleanedBase64 = base64data.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");

        document.getElementById('loader').style.display = "block"; // Show loader

        fetch('https://11gooofqbg.execute-api.us-east-1.amazonaws.com/prod/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ image: cleanedBase64 })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); // Log data for debugging
            document.getElementById('loader').style.display = "none"; // Hide loader
            if (data.patient_info) {
                displayPatientInfo(data.patient_info);
            }
            if (data.visits) {
                displayVisits(data.visits);
            }
            var responseData = data.message || JSON.stringify(data);
            document.getElementById('response').innerHTML = responseData.replace(/"/g, '');

            // Change the color of the response message based on the content
            if (responseData.includes("Denied")) {
                document.getElementById('response').style.color = "red";
                document.getElementById('response').style.fontWeight = "bold";
            } else if (responseData.includes("Welcome")) {
                document.getElementById('response').style.color = "darkgreen";
                document.getElementById('response').style.fontWeight = "bold";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('response').innerText = 'Failed to process the image.';
            document.getElementById('loader').style.display = "none"; // Hide loader
            document.getElementById('response').style.color = "red";
        });
    };

    reader.onerror = function (error) {
        console.log('Error: ', error);
        document.getElementById('response').innerText = 'Failed to load the image.';
        document.getElementById('loader').style.display = "none"; // Ensure loader is hidden on load error
    };

    reader.readAsDataURL(file);
}


var stream = null;

document.getElementById('startCamera').addEventListener('click', async function() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        document.getElementById('webcam').srcObject = stream;
        document.getElementById('webcam').style.display = 'block';
        document.getElementById('capture').style.display = 'inline';
        document.getElementById('retakePhoto').style.display = 'none';
        document.getElementById('submit').disabled = true;
    } catch (error) {
        console.log('Error accessing the webcam: ', error);
        document.getElementById('response').innerText = 'Webcam access denied.';
    }
});

document.getElementById('capture').addEventListener('click', function() {
    var video = document.getElementById('webcam');
    var canvas = document.getElementById('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    document.getElementById('uploadedImage').src = canvas.toDataURL();
    document.getElementById('uploadedImage').style.display = 'block';
    stream.getTracks().forEach(track => track.stop());
    document.getElementById('webcam').style.display = 'none';
    document.getElementById('retakePhoto').style.display = 'inline';
    document.getElementById('submit').disabled = false;
    document.getElementById('capture').style.display = 'none';
});

document.getElementById('retakePhoto').addEventListener('click', function() {
    document.getElementById('uploadedImage').style.display = 'none';
    startCamera();
    document.getElementById('capture').style.display = 'inline';
    document.getElementById('submit').disabled = true;
    document.getElementById('retakePhoto').style.display = 'none';
});

document.getElementById('submit').addEventListener('click', function() {
    document.getElementById('retakePhoto').style.display = 'none';
    document.getElementById('capture').style.display = 'none';
    if (document.getElementById('uploadedImage').src !== '') {
        document.getElementById('response').innerText = 'Processing...'; // Display loading message
        sendImageToServer(document.getElementById('canvas').toDataURL());
        
    }
    document.getElementById('startCamera').style.display = 'none';
});

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        document.getElementById('webcam').srcObject = stream;
        document.getElementById('webcam').style.display = 'block';
    });
}
function sendImageToServer(base64data) {
    var cleanedBase64 = base64data.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
    document.getElementById('loader').style.display = "block"; // Show the loader

    fetch('https://11gooofqbg.execute-api.us-east-1.amazonaws.com/prod/upload', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ image: cleanedBase64 })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loader').style.display = "none"; // Hide loader

        if (data.message.includes("Welcome")) {
            displayPatientInfo(data.patient_info);
            displayVisits(data.visits);
        }

        document.getElementById('response').innerText = data.message;
        if (data.message.includes("Denied")) {
            document.getElementById('response').style.color = "red";
            document.getElementById('response').style.fontWeight = "bold";
        } else if (data.message.includes("Welcome")) {
            document.getElementById('response').style.color = "darkgreen";
            document.getElementById('response').style.fontWeight = "bold";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('response').innerText = 'Failed to process the image.';
        document.getElementById('loader').style.display = "none"; // Hide loader
    });
}

function displayPatientInfo(patientInfo) {
    if (Object.keys(patientInfo).length > 0) {
        document.getElementById('patientDetails').style.display = 'block'; // Show the patient details section
        
        let tableContent = `
            <tr>
                <td><b>Name</b></td>
                <td>${patientInfo.name}</td>
            </tr>
            <tr>
                <td><b>Age</b></td>
                <td>${patientInfo.age}</td>
            </tr>
            <tr>
                <td><b>Blood Group</b></td>
                <td>${patientInfo.blood_group}</td>
            </tr>
            <tr>
                <td><b>Phone Number</b></td>
                <td>${patientInfo.phone_number}</td>
            </tr>
            <tr>
                <td><b>Address</b></td>
                <td>${patientInfo.address}</td>
            </tr>
            <tr>
                <td><b>Emergency Contact</b></td>
                <td>${patientInfo.emergency_contact}</td>
            </tr>`;

        document.getElementById('patientDetailsTable').innerHTML = tableContent;
    }
    adjustButtonSize();
}


function displayVisits(visits) {
    if (visits.length > 0) {
        document.getElementById('visitDetails').style.display = 'block'; // Show the visits section
        let tbody = document.querySelector('#visitDetails table tbody');
        tbody.innerHTML = ''; // Clear previous entries

        visits.forEach(visit => {
            let row = `<tr>
                <td>${visit.Date_of_Visit}</td>
                <td>${visit.Hospital_Name}</td>
                <td>${visit.Doctor_Name}</td>
                <td>${visit.Blood_Sugar_Level}</td>
                <td>${visit.Blood_Pressure_Level}</td>
                <td>${visit.Reason_for_visit}</td>
                <td>${visit.Medications_Prescribed}</td>
                <td>${visit.Doctor_Comments}</td>
                <td><a href="${visit.report_url}" target="_blank">View Report</a></td>
            </tr>`;
            tbody.innerHTML += row;
        });
    }
    adjustButtonSize();
}

function resetPage() {
    document.getElementById('patientDetails').style.display = 'none'; // Hide patient details section
    document.getElementById('visitDetails').style.display = 'none'; // Hide visits section
    document.getElementById('uploadedImage').style.display = 'none';
    document.getElementById('uploadedImage').src = '';
    document.getElementById('response').innerText = '';
    document.getElementById('response').style.color = ''; // Reset style
    document.getElementById('response').style.fontWeight = ''; // Reset style
    document.getElementById('imageUpload').value = '';
    document.getElementById('startCamera').style.display = 'inline';
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        document.getElementById('webcam').style.display = 'none';
    }
    ['capture', 'retakePhoto'].forEach(id => {
        document.getElementById(id).style.display = 'none';
    });
    document.getElementById('submit').disabled = true;
}


function adjustButtonSize() {
    let buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.style.minWidth = '150px';  // Adjust minWidth according to your design needs
        button.style.maxWidth = '200px';
    });
}

