<template>
  <div class="damage-upload">
    <div class="card">
      <h1>Upload Slika Šteta</h1>

      <div v-if="success" class="alert alert-success">
        {{ success }}
      </div>

      <div v-if="error" class="alert alert-error">
        {{ error }}
      </div>

      <form @submit.prevent="uploadFile" class="upload-form">
        <div class="form-group">
          <label for="file">Odaberite sliku</label>
          <input
            id="file"
            type="file"
            accept="image/*"
            @change="handleFileChange"
            required
          />
          <small>Podržani formati: JPG, PNG, GIF</small>
        </div>

        <div v-if="preview" class="preview">
          <img :src="preview" alt="Preview" />
        </div>

        <button type="submit" class="btn" :disabled="loading || !file">
          {{ loading ? "Uploadam..." : "📤 Upload sliku" }}
        </button>
      </form>

      <div class="info-box">
        <h3>ℹ️ Kako radi upload?</h3>
        <ol>
          <li>Odaberete sliku štete na vozilu</li>
          <li>Slika se uploada na LocalStack S3 bucket</li>
          <li>Vraća se URL slike za pregled</li>
        </ol>
        <p><strong>S3 Bucket:</strong> <code>stete-bucket</code></p>
      </div>

      <div v-if="uploadResult" class="upload-result">
        <h3>✅ Upload uspješan</h3>
        <div class="result-content">
          <p>
            <strong>Status:</strong>
            <span class="badge-success">{{ uploadResult.status }}</span>
          </p>
          <p><strong>Poruka:</strong> {{ uploadResult.message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import api from "../api";

export default {
  name: "DamageUpload",
  setup() {
    const file = ref(null);
    const preview = ref(null);
    const loading = ref(false);
    const success = ref("");
    const error = ref("");
    const uploadResult = ref(null);

    const handleFileChange = (event) => {
      const selectedFile = event.target.files[0];
      if (selectedFile) {
        file.value = selectedFile;

        const reader = new FileReader();
        reader.onload = (e) => {
          preview.value = e.target.result;
        };
        reader.readAsDataURL(selectedFile);
      }
    };

    const uploadFile = async () => {
      if (!file.value) return;

      loading.value = true;
      success.value = "";
      error.value = "";

      try {
        const response = await api.uploadDamage(file.value);
        uploadResult.value = response.data;
        success.value = "✅ Slika uspješno uploadana na S3!";

        file.value = null;
        preview.value = null;
        document.getElementById("file").value = "";
      } catch (err) {
        error.value = err.response?.data?.detail || "Greška pri uploadu slike";
        console.error("Upload error:", err);
      } finally {
        loading.value = false;
      }
    };

    return {
      file,
      preview,
      loading,
      success,
      error,
      uploadResult,
      handleFileChange,
      uploadFile,
    };
  },
};
</script>

<style scoped>
.damage-upload h1 {
  color: #333;
  margin-bottom: 1.5rem;
}

.upload-form {
  max-width: 600px;
}

.form-group small {
  display: block;
  color: #666;
  margin-top: 0.5rem;
}

.preview {
  margin: 1.5rem 0;
  text-align: center;
}

.preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.info-box {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 1.5rem;
  border-radius: 5px;
  margin-top: 2rem;
}

.info-box h3 {
  color: #856404;
  margin-bottom: 1rem;
}

.info-box ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.info-box li {
  margin-bottom: 0.5rem;
  color: #333;
}

.info-box code {
  background: #333;
  color: #0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.9rem;
}

.upload-result {
  background: #f0f9ff;
  border: 2px solid #667eea;
  padding: 1.5rem;
  border-radius: 10px;
  margin-top: 2rem;
}

.upload-result h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

.result-content p {
  margin-bottom: 0.75rem;
  color: #333;
}

.badge-success {
  background: #10b981;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
}
</style>
