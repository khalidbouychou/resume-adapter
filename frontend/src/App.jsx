import { useState, useEffect } from 'react'
import { Upload, Link2, FileText, Loader2 } from 'lucide-react'
import { Button } from './components/Button'
import { Input } from './components/Input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './components/Card'

function App() {
  const [cvFile, setCvFile] = useState(null)
  const [jobUrl, setJobUrl] = useState('')
  const [latexCode, setLatexCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [retrySeconds, setRetrySeconds] = useState(0)
  const [autoRetry, setAutoRetry] = useState(false)

  useEffect(() => {
    if (retrySeconds <= 0) return
    const timer = setInterval(() => {
      setRetrySeconds((s) => (s > 0 ? s - 1 : 0))
    }, 1000)
    return () => clearInterval(timer)
  }, [retrySeconds])

  // Auto-retry once countdown completes
  useEffect(() => {
    if (autoRetry && retrySeconds === 0) {
      setAutoRetry(false)
      // Re-run generate when timer finishes
      handleGenerate()
    }
  }, [autoRetry, retrySeconds])

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Please upload a PDF file')
        return
      }
      setCvFile(file)
      setError('')
    }
  }

  const handleGenerate = async () => {
    if (!cvFile) {
      setError('Please upload a CV file')
      return
    }
    if (!jobUrl) {
      setError('Please enter a LinkedIn job URL')
      return
    }

    setIsLoading(true)
    setError('')
    setLatexCode('')

    try {
      const formData = new FormData()
      formData.append('cv_file', cvFile)
      formData.append('job_url', jobUrl)

      const response = await fetch('/api/generate-resume', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to generate resume')
      }

      const data = await response.json()
      setLatexCode(data.latex_code)
    } catch (err) { 
      const msg = err.message || 'An error occurred while generating the resume'
      setError(msg)
      if (msg.includes('The service is busy right now')) {
        setRetrySeconds(60)
        setAutoRetry(true)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(latexCode)
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Resume Adapter</h1>
          <p className="text-gray-600">Generate tailored LaTeX resumes from your CV and job offers</p>
        </div>

        {/* Main Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Upload & Generate</CardTitle>
            <CardDescription>
              Upload your CV and provide a LinkedIn job URL to generate an adapted resume
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* File Upload */}
            <div className="space-y-2">
              <label className="text-sm font-medium">CV File (PDF)</label>
              <div className="flex items-center gap-4">
                <label className="flex-1 cursor-pointer">
                  <div className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors">
                    <div className="text-center">
                      <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        {cvFile ? cvFile.name : 'Click to upload PDF'}
                      </p>
                    </div>
                  </div>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Job URL Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">LinkedIn Job URL</label>
              <div className="flex items-center gap-2">
                <Link2 className="h-5 w-5 text-gray-400" />
                <Input
                  type="url"
                  placeholder="https://www.linkedin.com/jobs/view/..."
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
                <p className="text-sm text-red-600">{error}</p>
                {retrySeconds > 0 && (
                  <p className="mt-2 text-sm text-gray-600">Please wait {retrySeconds}s before retrying.</p>
                )}
              </div>
            )}

            {/* Generate Button */}
            <Button
              onClick={handleGenerate}
              disabled={isLoading || retrySeconds > 0}
              size="lg"
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  {retrySeconds > 0 ? `Please wait ${retrySeconds}s` : 'Generate Adapted Resume'}
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Output Card */}
        {latexCode && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Generated LaTeX Code</CardTitle>
                  <CardDescription>
                    Copy this code and compile it with a LaTeX editor
                  </CardDescription>
                </div>
                <Button onClick={copyToClipboard} variant="outline">
                  Copy Code
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <pre className="p-4 bg-gray-50 rounded-lg overflow-x-auto max-h-96 border border-gray-200">
                  <code className="text-sm font-mono">{latexCode}</code>
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Powered by OpenAI GPT-4 and RAG technology</p>
        </div>
      </div>
    </div>
  )
}

export default App
