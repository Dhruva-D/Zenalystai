import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Upload, File, Folder, Plus, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";
import { Navbar, FloatingScrollToTop } from "@/components/layout";
import { createApiEndpoint } from "@/lib/api";

export const UploadData = () => {
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [uploadedFolders, setUploadedFolders] = useState<FileList | null>(null);
  const [companyName, setCompanyName] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const newFiles = Array.from(e.dataTransfer.files);
      
      // Check if any of the files are from a folder (have a path with directory structure)
      const hasFolder = newFiles.some(file => (file as any).webkitRelativePath && (file as any).webkitRelativePath.includes('/'));
      
      if (hasFolder) {
        // Handle as folder upload
        setUploadedFolders(e.dataTransfer.files);
        setUploadedFiles([]); // Clear individual files when folder is uploaded
      } else {
        // Handle as individual files
        setUploadedFiles(prev => [...prev, ...newFiles]);
      }
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const newFiles = Array.from(e.target.files);
      setUploadedFiles(prev => [...prev, ...newFiles]);
      setUploadedFolders(null); // Clear folders when files are selected
    }
  };

  const handleFolderInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedFolders(e.target.files);
      setUploadedFiles([]); // Clear individual files when folder is selected
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const processFiles = async () => {
    setIsUploading(true);
    setUploadStatus("Uploading files...");
    
    try {
      const formData = new FormData();
      
      // Add individual files
      if (uploadedFiles.length > 0) {
        uploadedFiles.forEach((file) => {
          formData.append('files', file);
        });
      }
      
      // Add folder files
      if (uploadedFolders) {
        Array.from(uploadedFolders).forEach((file) => {
          formData.append('files', file);
        });
      }
      
      // Add company name if provided
      if (companyName.trim()) {
        formData.append('company_name', companyName.trim());
      } else {
        formData.append('company_name', 'Your Business');
      }
      
      // Upload files
      const uploadResponse = await fetch(createApiEndpoint('/upload/files'), {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        throw new Error('Upload failed');
      }
      
      const uploadResult = await uploadResponse.json();
      const sessionId = uploadResult.session_id;
      
      setUploadStatus("Processing files...");
      
      // Process uploaded files
      const processResponse = await fetch(createApiEndpoint(`/process/uploaded-files/${sessionId}`), {
        method: 'POST',
      });
      
      if (!processResponse.ok) {
        throw new Error('Processing failed');
      }
      
      const processResult = await processResponse.json();
      
      setUploadStatus("Redirecting to analysis...");
      
      // Redirect to analyze page with session ID
      setTimeout(() => {
        navigate(`/analyze?session_id=${sessionId}&company=${encodeURIComponent(processResult.company_name)}`);
      }, 1000);
      
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus("Upload failed. Please try again.");
      setIsUploading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 pt-24 pb-12 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-20 right-20 w-96 h-96 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.1, 0.2, 0.1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          className="absolute bottom-20 left-20 w-96 h-96 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full blur-3xl"
        />
      </div>
      <div className="container max-w-6xl mx-auto px-4 relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Upload Your{" "}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Data Files
            </span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            Upload Excel files, PDFs, or entire folders to start your personalized data analysis
          </p>
          
          {/* Company Name Input */}
          <div className="max-w-md mx-auto mb-8">
            <Label htmlFor="company-name" className="text-left block mb-2 text-sm font-medium">
              Company Name (Optional)
            </Label>
            <Input
              id="company-name"
              type="text"
              placeholder="Enter your company name..."
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="text-center"
              disabled={isUploading}
            />
            <p className="text-xs text-muted-foreground mt-2">
              This will personalize your analysis reports
            </p>
          </div>
        </motion.div>

        {/* Single Upload Area */}
        <Card className="border-2 border-dashed border-gray-300 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-8">
            {/* Drag & Drop Area */}
            <motion.div
              className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
                dragActive
                  ? "border-blue-500 bg-blue-50/50"
                  : "border-gray-300 hover:border-blue-400"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Hidden inputs for both files and folders */}
              <input
                id="file-upload"
                type="file"
                multiple
                onChange={handleFileInput}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".xlsx,.xls,.pdf,.csv"
                style={{ display: 'none' }}
              />
              <input
                id="folder-upload"
                type="file"
                onChange={handleFolderInput}
                {...({ webkitdirectory: '', directory: '' } as any)}
                multiple
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                style={{ display: 'none' }}
              />
              
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center"
              >
                <Upload className="w-8 h-8 text-white" />
              </motion.div>
              
              <h3 className="text-2xl font-semibold mb-2">Drop files or folders here</h3>
              <p className="text-muted-foreground mb-6">
                or choose your upload method below
              </p>
              
              {/* Upload Options */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-4">
                <Button
                  variant="outline"
                  onClick={() => document.getElementById('file-upload')?.click()}
                  className="flex items-center gap-2"
                >
                  <File className="w-4 h-4" />
                  Choose Files
                </Button>
                <span className="text-muted-foreground">or</span>
                <Button
                  variant="outline"
                  onClick={() => document.getElementById('folder-upload')?.click()}
                  className="flex items-center gap-2"
                >
                  <Folder className="w-4 h-4" />
                  Choose Folder
                </Button>
              </div>
              
              <p className="text-sm text-muted-foreground">
                Supports: Excel (.xlsx, .xls), PDF, CSV files
              </p>
            </motion.div>

            {/* File List */}
            {uploadedFiles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8"
              >
                <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Uploaded Files ({uploadedFiles.length})
                </h4>
                <div className="space-y-3">
                  {uploadedFiles.map((file, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm border"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <File className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{file.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Folder Display */}
            {uploadedFolders && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8"
              >
                <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  Folder Selected ({uploadedFolders.length} files)
                </h4>
                <div className="bg-white rounded-lg p-4 border">
                  <p className="font-medium">Folder uploaded successfully!</p>
                  <p className="text-sm text-muted-foreground">
                    {uploadedFolders.length} files ready for processing
                  </p>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        {(uploadedFiles.length > 0 || uploadedFolders) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center gap-4 mt-8"
          >
            {uploadStatus && (
              <div className="text-center mb-4">
                <p className="text-sm text-muted-foreground">{uploadStatus}</p>
                {isUploading && (
                  <div className="flex items-center justify-center gap-2 mt-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Processing...</span>
                  </div>
                )}
              </div>
            )}
            
            <div className="flex gap-4">
              <Button
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8"
                onClick={processFiles}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Process Files & Analyze
                    <Plus className="ml-2 w-5 h-5" />
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => {
                  setUploadedFiles([]);
                  setUploadedFolders(null);
                  setUploadStatus("");
                }}
                disabled={isUploading}
              >
                Clear All
              </Button>
            </div>
          </motion.div>
        )}

        {/* Info Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          {[
            {
              icon: File,
              title: "Supported Formats",
              description: "Excel, PDF, CSV files",
              color: "from-blue-500 to-cyan-500"
            },
            {
              icon: Upload,
              title: "Bulk Upload",
              description: "Upload multiple files at once",
              color: "from-purple-500 to-pink-500"
            },
            {
              icon: CheckCircle,
              title: "Auto Processing",
              description: "Automatic data extraction",
              color: "from-green-500 to-emerald-500"
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + index * 0.1 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
      </div>
      <FloatingScrollToTop />
    </>
  );
};