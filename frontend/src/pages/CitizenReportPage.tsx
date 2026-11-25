import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { DetectionResult, DuplicateCandidate, IssueCategory } from '../types';
import { 
  Camera, Upload, MapPin, CheckCircle, AlertTriangle, 
  ArrowRight, Sparkles, Shield, RefreshCw, Check, XCircle 
} from 'lucide-react';

const SAMPLE_IMAGES = [
  { label: 'Pothole', path: '/static/samples/pothole_sample.jpg', code: 'pothole' },
  { label: 'Road Crack', path: '/static/samples/road_crack_sample.jpg', code: 'road_crack' },
  { label: 'Garbage Pile', path: '/static/samples/garbage_pile_sample.jpg', code: 'garbage_pile' },
  { label: 'Damaged Streetlight', path: '/static/samples/damaged_streetlight_sample.jpg', code: 'damaged_streetlight' },
  { label: 'Damaged Guardrail', path: '/static/samples/damaged_infrastructure_sample.jpg', code: 'damaged_infrastructure' },
];

export const CitizenReportPage: React.FC = () => {
  const navigate = useNavigate();

  // Wizard Step
  const [step, setStep] = useState<1 | 2 | 3>(1);
  
  // Media State
  const [imageUrl, setImageUrl] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // AI Detection State
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [categories, setCategories] = useState<IssueCategory[]>([]);

  // Geospatial & Report State
  const [latitude, setLatitude] = useState<number>(12.9716);
  const [longitude, setLongitude] = useState<number>(77.5946);
  const [addressText, setAddressText] = useState<string>('MG Road Cross, Metro Corridor');
  const [citizenComment, setCitizenComment] = useState<string>('');
  const [consentGiven, setConsentGiven] = useState<boolean>(true);
  
  // Duplicates State
  const [duplicateCandidates, setDuplicateCandidates] = useState<DuplicateCandidate[]>([]);
  const [isCheckingDuplicates, setIsCheckingDuplicates] = useState(false);

  // Submission State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdReport, setCreatedReport] = useState<any>(null);

  useEffect(() => {
    api.get('/categories').then((res) => setCategories(res.data)).catch(console.error);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(pos.coords.latitude);
          setLongitude(pos.coords.longitude);
        },
        () => console.log('Location permission denied or unavailable, using urban default.')
      );
    }
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setUploadError(null);
    try {
      const res = await api.post('/uploads', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setImageUrl(res.data.image_url);
      runAiDetection(res.data.image_url);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || 'Failed to upload image.');
    } finally {
      setIsUploading(false);
    }
  };

  const runAiDetection = async (url: string) => {
    setIsDetecting(true);
    try {
      const formData = new URLSearchParams();
      formData.append('image_url', url);
      const res = await api.post('/detect', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      setDetectionResult(res.data);
      if (res.data.suggested_category) {
        setSelectedCategory(res.data.suggested_category);
        checkDuplicates(url, res.data.suggested_category);
      } else {
        setSelectedCategory(''); // Don't auto-guess if no defect detected
      }
      setStep(2);
    } catch (err) {
      console.error('Detection failed:', err);
      setSelectedCategory('');
      setStep(2);
    } finally {
      setIsDetecting(false);
    }
  };

  const checkDuplicates = async (imgUrl: string, catCode: string) => {
    setIsCheckingDuplicates(true);
    try {
      const res = await api.post('/duplicates/check', {
        latitude,
        longitude,
        category_code: catCode,
        image_url: imgUrl,
      });
      setDuplicateCandidates(res.data);
    } catch (err) {
      console.error('Error checking duplicates:', err);
    } finally {
      setIsCheckingDuplicates(false);
    }
  };

  const handleSelectSample = (samplePath: string, code: string) => {
    setImageUrl(samplePath);
    setSelectedCategory(code);
    runAiDetection(samplePath);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategory) {
      alert('Please select a civic issue category to submit this report.');
      return;
    }
    if (!consentGiven) {
      alert('Please agree to civic data processing consent to proceed.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        latitude,
        longitude,
        address_text: addressText,
        image_url: imageUrl,
        citizen_category_suggestion: categories.find(c => c.code === selectedCategory)?.display_name || selectedCategory,
        citizen_comment: citizenComment,
        consent_given: consentGiven,
        confirmed_category_code: selectedCategory,
      };

      const res = await api.post('/reports', payload);
      setCreatedReport(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit report.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const hasDetections = detectionResult && detectionResult.detections && detectionResult.detections.length > 0;

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
      <div className="mb-8 space-y-2 text-center">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-civic-50 text-civic-700 text-xs font-semibold border border-civic-200">
          <Camera className="w-3.5 h-3.5" />
          <span>Citizen Reporting Portal</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Report a Civic Problem</h1>
        <p className="text-sm text-slate-600 max-w-lg mx-auto">
          Snap or upload a photo. Our AI identifies the hazard, prevents duplicates, and calculates triage urgency.
        </p>

        {/* Wizard Steps indicator */}
        <div className="flex items-center justify-center gap-2 pt-4">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold ${step >= 1 ? 'bg-civic-600 text-white' : 'bg-slate-100 text-slate-500'}`}>
            <span>1. Capture Photo</span>
          </div>
          <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold ${step >= 2 ? 'bg-civic-600 text-white' : 'bg-slate-100 text-slate-500'}`}>
            <span>2. AI Verification</span>
          </div>
          <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold ${step >= 3 ? 'bg-civic-600 text-white' : 'bg-slate-100 text-slate-500'}`}>
            <span>3. Submit & Triage</span>
          </div>
        </div>
      </div>

      {createdReport ? (
        /* Submission Success Card */
        <div className="bg-white rounded-2xl border border-emerald-200 p-8 shadow-sm text-center space-y-6">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-slate-900">Report Successfully Submitted!</h2>
            <p className="text-sm text-slate-600 max-w-md mx-auto">
              Your submission has been cataloged and integrated into municipal dispatch intelligence.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 inline-block text-left text-xs space-y-1.5">
            <div><span className="font-semibold text-slate-700">Citizen Report Code:</span> <span className="font-mono font-bold text-civic-600">{createdReport.report_code}</span></div>
            <div><span className="font-semibold text-slate-700">Assigned Civic Issue:</span> <span className="font-mono text-slate-900">{createdReport.issue_id ? 'Linked' : 'Processing'}</span></div>
            <div><span className="font-semibold text-slate-700">Location:</span> {createdReport.address_text || `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`}</div>
          </div>

          <div className="flex justify-center gap-3">
            <button
              onClick={() => navigate(`/issues/${createdReport.issue_id}`)}
              className="px-5 py-2.5 bg-civic-600 hover:bg-civic-700 text-white rounded-xl text-sm font-semibold shadow-sm transition"
            >
              Track Live Issue Details
            </button>
            <button
              onClick={() => {
                setCreatedReport(null);
                setStep(1);
                setImageUrl('');
                setDetectionResult(null);
                setSelectedCategory('');
              }}
              className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-sm font-semibold transition"
            >
              Submit Another Report
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-8">
          {/* STEP 1: Upload or Select Sample */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-slate-300 hover:border-civic-500 rounded-2xl p-8 text-center transition bg-slate-50/50">
                <input
                  type="file"
                  id="image-upload"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <label htmlFor="image-upload" className="cursor-pointer block space-y-3">
                  <div className="w-12 h-12 rounded-xl bg-civic-100 text-civic-600 flex items-center justify-center mx-auto">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-sm font-semibold text-civic-600 hover:text-civic-700">
                      Click to upload an image
                    </span>
                    <span className="text-xs text-slate-500 block mt-1">JPEG, PNG, or WebP up to 15MB</span>
                  </div>
                  <div className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
                    <Shield className="w-3.5 h-3.5 text-emerald-500" />
                    <span>EXIF metadata automatically stripped for privacy</span>
                  </div>
                </label>
              </div>

              {isUploading && (
                <div className="flex items-center justify-center gap-2 text-sm text-civic-600 font-medium">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Sanitizing and uploading image...</span>
                </div>
              )}

              {/* Evaluator 1-Click Samples */}
              <div className="pt-4 border-t border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Or Select Instant Test Photo (For Competition Evaluation)
                  </span>
                  <span className="text-[11px] text-civic-600 font-medium">1-Click AI Demo</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  {SAMPLE_IMAGES.map((sample) => (
                    <button
                      key={sample.code}
                      type="button"
                      onClick={() => handleSelectSample(sample.path, sample.code)}
                      className="p-2.5 rounded-xl border border-slate-200 hover:border-civic-500 bg-white hover:bg-civic-50/50 text-left transition text-xs font-semibold text-slate-800 shadow-xs flex flex-col justify-between h-20"
                    >
                      <span className="line-clamp-2">{sample.label}</span>
                      <span className="text-[10px] text-civic-600 font-mono flex items-center gap-1">
                        <Sparkles className="w-3 h-3" /> Auto-Detect
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: AI Computer Vision Verification */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Visual Preview */}
                <div className="space-y-2">
                  <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Computer Vision Analysis Overlay
                  </div>
                  <div className="relative rounded-xl overflow-hidden border border-slate-200 bg-slate-900 aspect-4/3 flex items-center justify-center">
                    <img
                      src={detectionResult?.preview_url || imageUrl}
                      alt="Defect Preview"
                      className="w-full h-full object-contain"
                    />
                    {isDetecting && (
                      <div className="absolute inset-0 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center text-white text-xs font-medium gap-2">
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Running Computer Vision Model...</span>
                      </div>
                    )}
                  </div>
                  {detectionResult && (
                    <div className="flex items-center justify-between text-[11px] text-slate-500 px-1 font-mono">
                      <span>Model: {detectionResult.model_version}</span>
                      <span>Latency: {detectionResult.inference_ms}ms</span>
                    </div>
                  )}
                </div>

                {/* AI Classification & Category Choice */}
                <div className="space-y-4">
                  {/* AI Results Banner */}
                  {hasDetections ? (
                    <div className="bg-emerald-50/70 p-4 rounded-xl border border-emerald-200 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle className="w-4 h-4 text-emerald-600" />
                          <span>AI Defect Detected</span>
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          detectionResult?.confidence_tier === 'HIGH' ? 'bg-emerald-200 text-emerald-900' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {detectionResult?.confidence_tier} CONFIDENCE
                        </span>
                      </div>

                      <div className="space-y-2">
                        {detectionResult?.detections.map((det, idx) => (
                          <div key={idx} className="flex items-center justify-between bg-white p-2.5 rounded-lg border border-emerald-200 text-xs shadow-2xs">
                            <span className="font-semibold text-slate-800">{det.category_name}</span>
                            <span className="font-mono font-bold text-emerald-700">{Math.round(det.confidence * 100)}% Confidence</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    /* Doodles / Non-Civic / Clean Surface Alert */
                    <div className="bg-amber-50 p-4 rounded-xl border border-amber-200 space-y-2">
                      <div className="flex items-center gap-1.5 text-amber-800 font-bold text-xs">
                        <XCircle className="w-4 h-4 text-amber-600 shrink-0" />
                        <span>No Civic Defect Detected by AI</span>
                      </div>
                      <p className="text-xs text-amber-700 leading-relaxed">
                        {detectionResult?.detection_notes || "The AI inspected this photo and did not find an infrastructure defect (doodles, drawings, documents, or non-road photos are filtered out)."}
                      </p>
                      <p className="text-[11px] text-amber-600 italic">
                        If this photo represents a real municipal problem, please select the category below manually.
                      </p>
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-2">
                      {hasDetections ? 'Confirm or Correct Category:' : 'Select Category Manually:'}
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {categories.map((cat) => (
                        <button
                          key={cat.code}
                          type="button"
                          onClick={() => {
                            setSelectedCategory(cat.code);
                            checkDuplicates(imageUrl, cat.code);
                          }}
                          className={`p-2.5 rounded-xl border text-xs font-semibold text-left transition flex items-center justify-between ${
                            selectedCategory === cat.code
                              ? 'border-civic-600 bg-civic-50 text-civic-900 shadow-xs'
                              : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                          }`}
                        >
                          <span>{cat.display_name}</span>
                          {selectedCategory === cat.code && <Check className="w-4 h-4 text-civic-600" />}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition"
                    >
                      Change Photo
                    </button>
                    <button
                      type="button"
                      disabled={!selectedCategory}
                      onClick={() => setStep(3)}
                      className="flex-1 py-2 bg-civic-600 hover:bg-civic-700 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center justify-center gap-1.5 disabled:opacity-50"
                    >
                      <span>Proceed to Location & Submit</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Location, Duplicate Awareness & Final Submission */}
          {step === 3 && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {duplicateCandidates.length > 0 && duplicateCandidates[0].overall_duplicate_score >= 0.65 && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 space-y-2">
                  <div className="flex items-center gap-2 text-amber-800 font-bold text-xs">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Nearby Civic Issue Detected ({Math.round(duplicateCandidates[0].distance_meters)}m away)</span>
                  </div>
                  <p className="text-xs text-amber-700 leading-relaxed">
                    Our AI identified active complaint <span className="font-mono font-bold">{duplicateCandidates[0].issue_code}</span> at this vicinity. Submitting your report will increase the issue's community priority score to accelerate municipal response!
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Street Address / Landmark
                  </label>
                  <div className="relative">
                    <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      required
                      value={addressText}
                      onChange={(e) => setAddressText(e.target.value)}
                      placeholder="e.g. Near Metro Gate 2, Crossroad 4"
                      className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Latitude</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={latitude}
                      onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Longitude</label>
                    <input
                      type="number"
                      step="any"
                      required
                      value={longitude}
                      onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Citizen Observations / Notes (Optional)
                </label>
                <textarea
                  rows={3}
                  value={citizenComment}
                  onChange={(e) => setCitizenComment(e.target.value)}
                  placeholder="Describe severity, traffic blockage, or specific hazard details..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                />
              </div>

              {/* Privacy Consent */}
              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 flex items-start gap-3">
                <input
                  type="checkbox"
                  id="privacy-consent"
                  checked={consentGiven}
                  onChange={(e) => setConsentGiven(e.target.checked)}
                  className="mt-1 rounded border-slate-300 text-civic-600 focus:ring-civic-500"
                />
                <label htmlFor="privacy-consent" className="text-xs text-slate-600 cursor-pointer">
                  I consent to sharing this civic defect photo and GPS coordinates with municipal authorities for infrastructure repair. Photos will be publicly visible without personal metadata.
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="px-4 py-2.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold transition"
                >
                  Back to AI Verification
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !selectedCategory}
                  className="flex-1 py-3 bg-civic-600 hover:bg-civic-700 text-white rounded-xl text-sm font-semibold shadow-md transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Submitting to Municipal Registry...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      <span>Submit Citizen Report</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
};
