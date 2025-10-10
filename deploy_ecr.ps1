param(
  [Parameter(Mandatory=$true)][string]$AwsAccountId,
  [string]$Region = 'us-east-1',
  [string]$RepoName = 'meetingapp-web',
  [string]$LocalImage = 'meetingapp-web:latest',
  [string]$ImageTag = 'latest'
)

Write-Host "Building Docker image $LocalImage"
docker build -t $LocalImage .

$ecrUri = "$AwsAccountId.dkr.ecr.$Region.amazonaws.com/$RepoName`
"

Write-Host "Ensure ECR repository exists..."
try {
  aws ecr describe-repositories --repository-names $RepoName --region $Region | Out-Null
} catch {
  Write-Host "Repository not found, creating: $RepoName"
  aws ecr create-repository --repository-name $RepoName --region $Region | Out-Null
}

Write-Host "Logging in to ECR"
$login = aws ecr get-login-password --region $Region
$login | docker login --username AWS --password-stdin "$AwsAccountId.dkr.ecr.$Region.amazonaws.com"

$fullTag = "$ecrUri:$ImageTag"
Write-Host "Tagging image: $LocalImage -> $fullTag"
docker tag $LocalImage $fullTag

Write-Host "Pushing image to ECR: $fullTag"
docker push $fullTag

Write-Host "Image pushed: $fullTag"
