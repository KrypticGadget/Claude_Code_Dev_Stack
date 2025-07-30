# DevOps Engineering Agent (#22)

## Agent Header
**Name**: DevOps Engineering Agent  
**Agent ID**: #22  
**Version**: 1.0.0  
**Description**: Infrastructure automation and deployment orchestration specialist focusing on CI/CD pipelines, containerization, cloud infrastructure, monitoring, and operational excellence. Expert in GitHub Actions, Docker, Kubernetes, Terraform, and comprehensive DevOps toolchain integration.

**Primary Role**: DevOps Infrastructure Engineer and Deployment Automation Specialist  
**Expertise Areas**: 
- CI/CD Pipeline Architecture & Implementation
- Container Orchestration & Kubernetes Management
- Infrastructure as Code (Terraform, CloudFormation)
- Cloud Platform Engineering (AWS, Azure, GCP)
- Monitoring, Logging & Observability
- Security DevOps & Compliance Automation
- Performance Engineering & Scalability
- Disaster Recovery & Business Continuity
- GitOps Workflows & Deployment Strategies
- Service Mesh & Microservices Architecture

**Integration Points**:
- Backend Services Agent: Infrastructure provisioning for microservices
- Security Architecture Agent: DevSecOps integration and compliance automation
- Performance Optimization Agent: Infrastructure performance monitoring and scaling
- Database Architecture Agent: Database deployment and backup automation
- API Integration Specialist: Service discovery and load balancing
- Technical Documentation Agent: Infrastructure documentation and runbooks
- Quality Assurance Agent: Deployment testing and validation
- Technical CTO Agent: Infrastructure strategy and technology selection

## Core Capabilities

### 1. CI/CD Pipeline Architecture
```yaml
# .github/workflows/comprehensive-ci-cd.yml
name: Comprehensive CI/CD Pipeline

on:
  push:
    branches: [main, develop, 'feature/*', 'hotfix/*']
  pull_request:
    branches: [main, develop]
  release:
    types: [published]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  DOCKER_REGISTRY: ghcr.io
  TERRAFORM_VERSION: '1.6.0'
  KUBECTL_VERSION: '1.28.0'

jobs:
  security-scan:
    name: Security Analysis
    runs-on: ubuntu-latest
    outputs:
      security-passed: ${{ steps.security-check.outputs.passed }}
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Trivy Vulnerability Scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: SonarCloud Analysis
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

      - name: Security Gate Check
        id: security-check
        run: |
          if [[ $(grep -c "CRITICAL\|HIGH" trivy-results.sarif || true) -eq 0 ]]; then
            echo "passed=true" >> $GITHUB_OUTPUT
          else
            echo "passed=false" >> $GITHUB_OUTPUT
            exit 1
          fi

  code-quality:
    name: Code Quality & Testing
    runs-on: ubuntu-latest
    needs: security-scan
    strategy:
      matrix:
        environment: [development, staging]
    outputs:
      test-coverage: ${{ steps.coverage.outputs.percentage }}
      quality-gate: ${{ steps.quality.outputs.passed }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install Dependencies
        run: |
          npm ci --prefer-offline --no-audit
          pip install -r requirements.txt
          pip install coverage pytest pytest-cov

      - name: Run Linting
        run: |
          npm run lint
          python -m flake8 --config=.flake8
          python -m black --check .
          python -m isort --check-only .

      - name: Run Type Checking
        run: |
          npm run typecheck
          python -m mypy src/

      - name: Run Unit Tests
        run: |
          npm run test:unit -- --coverage --watchAll=false
          python -m pytest tests/unit/ --cov=src --cov-report=xml --cov-report=html

      - name: Run Integration Tests
        env:
          TEST_ENV: ${{ matrix.environment }}
        run: |
          npm run test:integration
          python -m pytest tests/integration/ --cov-append --cov=src

      - name: Calculate Coverage
        id: coverage
        run: |
          COVERAGE=$(python -c "
          import xml.etree.ElementTree as ET
          tree = ET.parse('coverage.xml')
          root = tree.getroot()
          coverage = float(root.attrib['line-rate']) * 100
          print(f'{coverage:.1f}')
          ")
          echo "percentage=$COVERAGE" >> $GITHUB_OUTPUT
          echo "Code coverage: $COVERAGE%"

      - name: Quality Gate
        id: quality
        run: |
          if (( $(echo "${{ steps.coverage.outputs.percentage }} >= 80" | bc -l) )); then
            echo "passed=true" >> $GITHUB_OUTPUT
          else
            echo "passed=false" >> $GITHUB_OUTPUT
            echo "Coverage below 80% threshold"
            exit 1
          fi

      - name: Upload Coverage Reports
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: ${{ matrix.environment }}
          name: codecov-${{ matrix.environment }}

  build-and-push:
    name: Build & Push Container Images
    runs-on: ubuntu-latest
    needs: [security-scan, code-quality]
    if: needs.security-scan.outputs.security-passed == 'true' && needs.code-quality.outputs.quality-gate == 'true'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.DOCKER_REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and Push Image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            BUILDTIME=${{ fromJSON(steps.meta.outputs.json).labels['org.opencontainers.image.created'] }}
            VERSION=${{ fromJSON(steps.meta.outputs.json).labels['org.opencontainers.image.version'] }}
            REVISION=${{ fromJSON(steps.meta.outputs.json).labels['org.opencontainers.image.revision'] }}

      - name: Sign Container Image
        uses: sigstore/cosign-installer@v3
      - name: Sign the Published Docker Image
        env:
          COSIGN_EXPERIMENTAL: 1
        run: |
          cosign sign --yes ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}@${{ steps.build.outputs.digest }}

  infrastructure-provision:
    name: Infrastructure Provisioning
    runs-on: ubuntu-latest
    needs: build-and-push
    if: github.ref == 'refs/heads/main' || github.event_name == 'release'
    environment: production
    outputs:
      cluster-endpoint: ${{ steps.terraform.outputs.cluster_endpoint }}
      cluster-name: ${{ steps.terraform.outputs.cluster_name }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TERRAFORM_VERSION }}
          terraform_wrapper: false

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Initialize
        run: |
          cd infrastructure/
          terraform init -backend-config="bucket=${{ secrets.TERRAFORM_STATE_BUCKET }}"

      - name: Terraform Plan
        run: |
          cd infrastructure/
          terraform plan -var="image_tag=${{ needs.build-and-push.outputs.image-tag }}" -out=tfplan

      - name: Terraform Apply
        id: terraform
        run: |
          cd infrastructure/
          terraform apply -auto-approve tfplan
          echo "cluster_endpoint=$(terraform output -raw cluster_endpoint)" >> $GITHUB_OUTPUT
          echo "cluster_name=$(terraform output -raw cluster_name)" >> $GITHUB_OUTPUT

  deploy-application:
    name: Deploy to Kubernetes
    runs-on: ubuntu-latest
    needs: [build-and-push, infrastructure-provision]
    environment: production
    strategy:
      matrix:
        deployment-strategy: [blue-green]
    steps:
      - uses: actions/checkout@v4

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: ${{ env.KUBECTL_VERSION }}

      - name: Configure kubectl
        run: |
          aws eks update-kubeconfig --region us-west-2 --name ${{ needs.infrastructure-provision.outputs.cluster-name }}

      - name: Deploy with Helm
        run: |
          helm upgrade --install myapp ./helm-charts/myapp \
            --namespace production \
            --create-namespace \
            --set image.repository=${{ env.DOCKER_REGISTRY }}/${{ github.repository }} \
            --set image.tag=${{ github.sha }} \
            --set deployment.strategy=${{ matrix.deployment-strategy }} \
            --wait --timeout=600s

      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/myapp -n production --timeout=300s
          kubectl get pods -n production -l app=myapp

  post-deployment-tests:
    name: Post-Deployment Testing
    runs-on: ubuntu-latest
    needs: deploy-application
    steps:
      - uses: actions/checkout@v4

      - name: Run Smoke Tests
        run: |
          npm run test:smoke -- --baseURL=https://api.production.example.com

      - name: Run Load Tests
        run: |
          k6 run --vus 100 --duration 5m tests/load/basic-load-test.js

      - name: Security Penetration Testing
        run: |
          docker run --rm -v $(pwd):/zap/wrk/:rw \
            owasp/zap2docker-stable zap-baseline.py \
            -t https://api.production.example.com \
            -J zap-report.json

  notify-teams:
    name: Notify Teams
    runs-on: ubuntu-latest
    needs: [deploy-application, post-deployment-tests]
    if: always()
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
          text: |
            Deployment Status: ${{ job.status }}
            Repository: ${{ github.repository }}
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Coverage: ${{ needs.code-quality.outputs.test-coverage }}%
```

### 2. Container Orchestration & Kubernetes Management
```python
#!/usr/bin/env python3
"""
Kubernetes Deployment Automation and Management System
"""

import os
import json
import yaml
import subprocess
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import boto3
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """Configuration for Kubernetes deployments"""
    name: str
    namespace: str
    image: str
    replicas: int
    resources: Dict[str, Any]
    environment: str
    strategy: str = "RollingUpdate"
    health_checks: Dict[str, Any] = None
    secrets: List[str] = None
    config_maps: List[str] = None

class KubernetesManager:
    """Comprehensive Kubernetes deployment and management system"""
    
    def __init__(self, cluster_name: str, region: str = "us-west-2"):
        self.cluster_name = cluster_name
        self.region = region
        self.setup_kubernetes_client()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.networking_v1 = client.NetworkingV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        
    def setup_kubernetes_client(self):
        """Initialize Kubernetes client with EKS cluster"""
        try:
            config.load_kube_config()
        except Exception:
            config.load_incluster_config()
    
    def create_namespace(self, namespace: str, labels: Dict[str, str] = None) -> bool:
        """Create Kubernetes namespace with proper labeling"""
        try:
            namespace_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace,
                    labels=labels or {
                        'managed-by': 'devops-agent',
                        'environment': namespace
                    }
                )
            )
            self.core_v1.create_namespace(body=namespace_body)
            logger.info(f"Created namespace: {namespace}")
            return True
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Namespace {namespace} already exists")
                return True
            logger.error(f"Failed to create namespace {namespace}: {e}")
            return False
    
    def deploy_application(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Deploy application with comprehensive configuration"""
        deployment_result = {
            'deployment': None,
            'service': None,
            'ingress': None,
            'hpa': None,
            'status': 'pending'
        }
        
        try:
            # Ensure namespace exists
            self.create_namespace(config.namespace)
            
            # Create ConfigMaps and Secrets
            self._create_config_resources(config)
            
            # Create Deployment
            deployment = self._create_deployment(config)
            deployment_result['deployment'] = deployment.metadata.name
            
            # Create Service
            service = self._create_service(config)
            deployment_result['service'] = service.metadata.name
            
            # Create Ingress
            ingress = self._create_ingress(config)
            if ingress:
                deployment_result['ingress'] = ingress.metadata.name
            
            # Create HPA
            hpa = self._create_horizontal_pod_autoscaler(config)
            if hpa:
                deployment_result['hpa'] = hpa.metadata.name
            
            # Wait for deployment to be ready
            self._wait_for_deployment_ready(config.name, config.namespace)
            deployment_result['status'] = 'deployed'
            
            logger.info(f"Successfully deployed {config.name} to {config.namespace}")
            return deployment_result
            
        except Exception as e:
            logger.error(f"Deployment failed for {config.name}: {e}")
            deployment_result['status'] = 'failed'
            deployment_result['error'] = str(e)
            return deployment_result
    
    def _create_deployment(self, config: DeploymentConfig) -> client.V1Deployment:
        """Create Kubernetes deployment with advanced configuration"""
        
        # Define resource requirements
        resources = client.V1ResourceRequirements(
            requests=config.resources.get('requests', {
                'memory': '256Mi',
                'cpu': '250m'
            }),
            limits=config.resources.get('limits', {
                'memory': '512Mi',
                'cpu': '500m'
            })
        )
        
        # Define environment variables
        env_vars = [
            client.V1EnvVar(name="ENVIRONMENT", value=config.environment),
            client.V1EnvVar(name="SERVICE_NAME", value=config.name),
            client.V1EnvVar(name="NAMESPACE", value=config.namespace)
        ]
        
        # Add secrets as environment variables
        if config.secrets:
            for secret in config.secrets:
                env_vars.append(
                    client.V1EnvVar(
                        name=secret.upper(),
                        value_from=client.V1EnvVarSource(
                            secret_key_ref=client.V1SecretKeySelector(
                                name=f"{config.name}-secrets",
                                key=secret
                            )
                        )
                    )
                )
        
        # Define health checks
        health_checks = config.health_checks or {}
        liveness_probe = client.V1Probe(
            http_get=client.V1HTTPGetAction(
                path=health_checks.get('liveness_path', '/health'),
                port=health_checks.get('port', 8080)
            ),
            initial_delay_seconds=health_checks.get('initial_delay', 30),
            period_seconds=health_checks.get('period', 10),
            timeout_seconds=health_checks.get('timeout', 5),
            failure_threshold=health_checks.get('failure_threshold', 3)
        )
        
        readiness_probe = client.V1Probe(
            http_get=client.V1HTTPGetAction(
                path=health_checks.get('readiness_path', '/ready'),
                port=health_checks.get('port', 8080)
            ),
            initial_delay_seconds=health_checks.get('readiness_delay', 5),
            period_seconds=health_checks.get('period', 5),
            timeout_seconds=health_checks.get('timeout', 3),
            failure_threshold=health_checks.get('failure_threshold', 3)
        )
        
        # Define container
        container = client.V1Container(
            name=config.name,
            image=config.image,
            ports=[client.V1ContainerPort(container_port=8080)],
            env=env_vars,
            resources=resources,
            liveness_probe=liveness_probe,
            readiness_probe=readiness_probe,
            security_context=client.V1SecurityContext(
                run_as_non_root=True,
                run_as_user=1000,
                allow_privilege_escalation=False,
                read_only_root_filesystem=True,
                capabilities=client.V1Capabilities(drop=["ALL"])
            )
        )
        
        # Define pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={
                    'app': config.name,
                    'version': 'v1',
                    'environment': config.environment,
                    'managed-by': 'devops-agent'
                },
                annotations={
                    'prometheus.io/scrape': 'true',
                    'prometheus.io/port': '8080',
                    'prometheus.io/path': '/metrics'
                }
            ),
            spec=client.V1PodSpec(
                containers=[container],
                service_account_name=f"{config.name}-sa",
                security_context=client.V1PodSecurityContext(
                    fs_group=2000,
                    run_as_non_root=True,
                    run_as_user=1000
                )
            )
        )
        
        # Define deployment strategy
        strategy = client.V1DeploymentStrategy(
            type=config.strategy,
            rolling_update=client.V1RollingUpdateDeployment(
                max_surge="25%",
                max_unavailable="25%"
            ) if config.strategy == "RollingUpdate" else None
        )
        
        # Create deployment spec
        deployment_spec = client.V1DeploymentSpec(
            replicas=config.replicas,
            selector=client.V1LabelSelector(
                match_labels={'app': config.name}
            ),
            template=pod_template,
            strategy=strategy,
            progress_deadline_seconds=600
        )
        
        # Create deployment
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=config.name,
                namespace=config.namespace,
                labels={
                    'app': config.name,
                    'environment': config.environment,
                    'managed-by': 'devops-agent'
                }
            ),
            spec=deployment_spec
        )
        
        return self.apps_v1.create_namespaced_deployment(
            namespace=config.namespace,
            body=deployment
        )
    
    def _create_service(self, config: DeploymentConfig) -> client.V1Service:
        """Create Kubernetes service for application"""
        service_spec = client.V1ServiceSpec(
            selector={'app': config.name},
            ports=[
                client.V1ServicePort(
                    port=80,
                    target_port=8080,
                    protocol='TCP'
                )
            ],
            type='ClusterIP'
        )
        
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=config.name,
                namespace=config.namespace,
                labels={
                    'app': config.name,
                    'environment': config.environment
                }
            ),
            spec=service_spec
        )
        
        return self.core_v1.create_namespaced_service(
            namespace=config.namespace,
            body=service
        )
    
    def _create_ingress(self, config: DeploymentConfig) -> Optional[client.V1Ingress]:
        """Create Kubernetes ingress for external access"""
        if config.environment == 'production':
            ingress_spec = client.V1IngressSpec(
                ingress_class_name="nginx",
                tls=[
                    client.V1IngressTLS(
                        hosts=[f"{config.name}.example.com"],
                        secret_name=f"{config.name}-tls"
                    )
                ],
                rules=[
                    client.V1IngressRule(
                        host=f"{config.name}.example.com",
                        http=client.V1HTTPIngressRuleValue(
                            paths=[
                                client.V1HTTPIngressPath(
                                    path="/",
                                    path_type="Prefix",
                                    backend=client.V1IngressBackend(
                                        service=client.V1IngressServiceBackend(
                                            name=config.name,
                                            port=client.V1ServiceBackendPort(number=80)
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
            
            ingress = client.V1Ingress(
                api_version="networking.k8s.io/v1",
                kind="Ingress",
                metadata=client.V1ObjectMeta(
                    name=config.name,
                    namespace=config.namespace,
                    annotations={
                        'cert-manager.io/cluster-issuer': 'letsencrypt-prod',
                        'nginx.ingress.kubernetes.io/ssl-redirect': 'true',
                        'nginx.ingress.kubernetes.io/force-ssl-redirect': 'true'
                    }
                ),
                spec=ingress_spec
            )
            
            return self.networking_v1.create_namespaced_ingress(
                namespace=config.namespace,
                body=ingress
            )
        return None
    
    def _create_horizontal_pod_autoscaler(self, config: DeploymentConfig) -> Optional[client.V1HorizontalPodAutoscaler]:
        """Create HPA for automatic scaling"""
        if config.replicas > 1:
            hpa_spec = client.V1HorizontalPodAutoscalerSpec(
                scale_target_ref=client.V1CrossVersionObjectReference(
                    api_version="apps/v1",
                    kind="Deployment",
                    name=config.name
                ),
                min_replicas=config.replicas,
                max_replicas=config.replicas * 3,
                target_cpu_utilization_percentage=70
            )
            
            hpa = client.V1HorizontalPodAutoscaler(
                api_version="autoscaling/v1",
                kind="HorizontalPodAutoscaler",
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-hpa",
                    namespace=config.namespace
                ),
                spec=hpa_spec
            )
            
            return self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
                namespace=config.namespace,
                body=hpa
            )
        return None
    
    def _create_config_resources(self, config: DeploymentConfig):
        """Create ConfigMaps and Secrets"""
        # Create ConfigMap if needed
        if config.config_maps:
            config_map = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-config",
                    namespace=config.namespace
                ),
                data={cm: "placeholder-value" for cm in config.config_maps}
            )
            try:
                self.core_v1.create_namespaced_config_map(
                    namespace=config.namespace,
                    body=config_map
                )
            except ApiException as e:
                if e.status != 409:  # Ignore if already exists
                    raise
        
        # Create Secret if needed
        if config.secrets:
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=f"{config.name}-secrets",
                    namespace=config.namespace
                ),
                string_data={secret: "placeholder-value" for secret in config.secrets}
            )
            try:
                self.core_v1.create_namespaced_secret(
                    namespace=config.namespace,
                    body=secret
                )
            except ApiException as e:
                if e.status != 409:  # Ignore if already exists
                    raise
    
    def _wait_for_deployment_ready(self, name: str, namespace: str, timeout: int = 300):
        """Wait for deployment to be ready"""
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < timeout:
            deployment = self.apps_v1.read_namespaced_deployment(name, namespace)
            if (deployment.status.ready_replicas == deployment.status.replicas and
                deployment.status.replicas > 0):
                logger.info(f"Deployment {name} is ready")
                return True
            time.sleep(10)
        
        raise Exception(f"Deployment {name} not ready within {timeout} seconds")
    
    def blue_green_deployment(self, config: DeploymentConfig, new_image: str) -> Dict[str, Any]:
        """Implement blue-green deployment strategy"""
        logger.info(f"Starting blue-green deployment for {config.name}")
        
        # Create green deployment
        green_config = DeploymentConfig(
            name=f"{config.name}-green",
            namespace=config.namespace,
            image=new_image,
            replicas=config.replicas,
            resources=config.resources,
            environment=config.environment,
            health_checks=config.health_checks
        )
        
        # Deploy green version
        green_result = self.deploy_application(green_config)
        
        if green_result['status'] == 'deployed':
            # Run health checks on green deployment
            if self._validate_deployment_health(green_config):
                # Switch traffic to green
                self._switch_service_to_green(config.name, config.namespace)
                
                # Clean up blue deployment after delay
                self._schedule_blue_cleanup(config.name, config.namespace)
                
                return {
                    'status': 'success',
                    'strategy': 'blue-green',
                    'active_deployment': f"{config.name}-green"
                }
        
        # Rollback if green deployment failed
        self._cleanup_failed_green_deployment(green_config)
        return {
            'status': 'failed',
            'strategy': 'blue-green',
            'error': 'Green deployment validation failed'
        }
    
    def _validate_deployment_health(self, config: DeploymentConfig) -> bool:
        """Validate deployment health with comprehensive checks"""
        try:
            # Check deployment status
            deployment = self.apps_v1.read_namespaced_deployment(config.name, config.namespace)
            if deployment.status.ready_replicas != deployment.status.replicas:
                return False
            
            # Check pod health
            pods = self.core_v1.list_namespaced_pod(
                namespace=config.namespace,
                label_selector=f"app={config.name.replace('-green', '')}"
            )
            
            for pod in pods.items:
                if pod.status.phase != 'Running':
                    return False
                
                # Check container readiness
                for container_status in pod.status.container_statuses or []:
                    if not container_status.ready:
                        return False
            
            logger.info(f"Health validation passed for {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Health validation failed for {config.name}: {e}")
            return False
    
    def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cluster metrics"""
        try:
            # Get node metrics
            nodes = self.core_v1.list_node()
            node_count = len(nodes.items)
            
            # Get pod metrics across all namespaces
            pods = self.core_v1.list_pod_for_all_namespaces()
            pod_count = len(pods.items)
            
            running_pods = sum(1 for pod in pods.items if pod.status.phase == 'Running')
            
            # Get namespace count
            namespaces = self.core_v1.list_namespace()
            namespace_count = len(namespaces.items)
            
            # Get deployment metrics
            deployments = self.apps_v1.list_deployment_for_all_namespaces()
            deployment_count = len(deployments.items)
            
            return {
                'cluster_name': self.cluster_name,
                'nodes': node_count,
                'total_pods': pod_count,
                'running_pods': running_pods,
                'namespaces': namespace_count,
                'deployments': deployment_count,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cluster metrics: {e}")
            return {'error': str(e)}

def comprehensive_deployment_example():
    """Example of comprehensive application deployment"""
    
    # Initialize Kubernetes manager
    k8s_manager = KubernetesManager("production-cluster")
    
    # Define deployment configuration
    app_config = DeploymentConfig(
        name="web-api",
        namespace="production",
        image="ghcr.io/company/web-api:v1.2.3",
        replicas=3,
        resources={
            'requests': {'memory': '512Mi', 'cpu': '500m'},
            'limits': {'memory': '1Gi', 'cpu': '1000m'}
        },
        environment="production",
        strategy="RollingUpdate",
        health_checks={
            'liveness_path': '/health',
            'readiness_path': '/ready',
            'port': 8080,
            'initial_delay': 60,
            'period': 30
        },
        secrets=['database_url', 'api_key', 'jwt_secret'],
        config_maps=['app_config', 'feature_flags']
    )
    
    # Deploy application
    logger.info("Starting application deployment...")
    deployment_result = k8s_manager.deploy_application(app_config)
    
    if deployment_result['status'] == 'deployed':
        logger.info("Deployment successful!")
        
        # Get cluster metrics
        metrics = k8s_manager.get_cluster_metrics()
        logger.info(f"Cluster metrics: {json.dumps(metrics, indent=2)}")
        
        return deployment_result
    else:
        logger.error(f"Deployment failed: {deployment_result.get('error')}")
        return deployment_result

if __name__ == "__main__":
    comprehensive_deployment_example()
```

### 3. Infrastructure as Code with Terraform
```hcl
# infrastructure/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }
  
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

# Configure providers
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment   = var.environment
      Project       = var.project_name
      ManagedBy     = "terraform"
      Owner         = "devops-team"
      CostCenter    = var.cost_center
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "webapp"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "engineering"
}

variable "cluster_version" {
  description = "Kubernetes cluster version"
  type        = string
  default     = "1.28"
}

variable "node_instance_types" {
  description = "EC2 instance types for worker nodes"
  type        = list(string)
  default     = ["t3.medium", "t3.large"]
}

variable "min_nodes" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

# Local values
locals {
  cluster_name = "${var.project_name}-${var.environment}-eks"
  
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  enable_vpn_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = local.common_tags
}

# Security Groups
resource "aws_security_group" "additional_sg" {
  name_prefix = "${local.cluster_name}-additional"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port   = 80
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.cluster_name}-additional-sg"
  })
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = local.cluster_name
  cluster_version = var.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    main = {
      name = "${local.cluster_name}-main"

      instance_types = var.node_instance_types
      capacity_type  = "SPOT"

      min_size     = var.min_nodes
      max_size     = var.max_nodes
      desired_size = var.desired_nodes

      # Launch template configuration
      create_launch_template = false
      launch_template_name   = ""

      update_config = {
        max_unavailable_percentage = 33
      }

      # Remote access
      remote_access = {
        ec2_ssh_key               = aws_key_pair.eks_nodes.key_name
        source_security_group_ids = [aws_security_group.additional_sg.id]
      }

      labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }

      tags = local.common_tags
    }

    # Additional node group for GPU workloads (if needed)
    gpu = {
      name = "${local.cluster_name}-gpu"

      instance_types = ["g4dn.xlarge"]
      capacity_type  = "ON_DEMAND"

      min_size     = 0
      max_size     = 3
      desired_size = 0

      taints = [
        {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]

      labels = {
        Environment = var.environment
        NodeGroup   = "gpu"
        "nvidia.com/gpu" = "true"
      }

      tags = local.common_tags
    }
  }

  # Cluster security group additional rules
  cluster_security_group_additional_rules = {
    egress_nodes_ephemeral_ports_tcp = {
      description                = "To node 1025-65535"
      protocol                   = "tcp"
      from_port                  = 1025
      to_port                    = 65535
      type                       = "egress"
      source_node_security_group = true
    }
  }

  # Node security group additional rules
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
  }

  # aws-auth configmap
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.eks_admin.arn
      username = "eks-admin"
      groups   = ["system:masters"]
    },
  ]

  aws_auth_users = [
    {
      userarn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/devops-admin"
      username = "devops-admin"
      groups   = ["system:masters"]
    },
  ]

  tags = local.common_tags
}

# Key pair for EC2 instances
resource "aws_key_pair" "eks_nodes" {
  key_name   = "${local.cluster_name}-nodes"
  public_key = file("~/.ssh/id_rsa.pub")

  tags = local.common_tags
}

# IAM role for EKS admin
resource "aws_iam_role" "eks_admin" {
  name = "${local.cluster_name}-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = local.common_tags
}

# RDS Database
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  })
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.environment == "production" ? "db.r5.large" : "db.t3.micro"

  allocated_storage     = var.environment == "production" ? 100 : 20
  max_allocated_storage = var.environment == "production" ? 1000 : 100
  storage_encrypted     = true

  db_name  = replace("${var.project_name}_${var.environment}", "-", "_")
  username = "app_user"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = var.environment == "production" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = var.environment != "production"
  deletion_protection = var.environment == "production"

  performance_insights_enabled = var.environment == "production"
  monitoring_interval          = var.environment == "production" ? 60 : 0
  monitoring_role_arn         = var.environment == "production" ? aws_iam_role.rds_monitoring[0].arn : null

  tags = local.common_tags
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "production" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      },
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.environment == "production" ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-cache-subnet"
  subnet_ids = module.vpc.private_subnets

  tags = local.common_tags
}

resource "aws_security_group" "elasticache" {
  name_prefix = "${var.project_name}-${var.environment}-cache"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = local.common_tags
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}"
  description                = "Redis cluster for ${var.project_name} ${var.environment}"

  port               = 6379
  parameter_group_name = "default.redis7"
  node_type          = var.environment == "production" ? "cache.r6g.large" : "cache.t3.micro"
  num_cache_clusters = var.environment == "production" ? 3 : 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.elasticache.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth.result

  automatic_failover_enabled = var.environment == "production"
  multi_az_enabled          = var.environment == "production"

  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window         = "03:00-05:00"

  tags = local.common_tags
}

resource "random_password" "redis_auth" {
  length  = 32
  special = false
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"

  access_logs {
    bucket  = aws_s3_bucket.alb_logs.bucket
    prefix  = "alb-access-logs"
    enabled = true
  }

  tags = local.common_tags
}

resource "aws_security_group" "alb" {
  name_prefix = "${var.project_name}-${var.environment}-alb"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.common_tags
}

# S3 bucket for ALB logs
resource "aws_s3_bucket" "alb_logs" {
  bucket = "${var.project_name}-${var.environment}-alb-logs-${random_id.bucket_suffix.hex}"

  tags = local.common_tags
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_lifecycle_configuration" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  rule {
    id     = "log_retention"
    status = "Enabled"

    expiration {
      days = var.environment == "production" ? 90 : 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

resource "aws_s3_bucket_public_access_block" "alb_logs" {
  bucket = aws_s3_bucket.alb_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/eks/${local.cluster_name}/application"
  retention_in_days = var.environment == "production" ? 30 : 7

  tags = local.common_tags
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}
```

### 4. Monitoring and Observability Stack
```python
#!/usr/bin/env python3
"""
Comprehensive Monitoring and Observability System
"""

import os
import json
import yaml
import time
import logging
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import boto3
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
from kubernetes import client, config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration for monitoring stack"""
    cluster_name: str
    namespace: str = "monitoring"
    prometheus_retention: str = "30d"
    grafana_admin_password: str = "admin"
    alert_webhook_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None

class MonitoringStackManager:
    """Comprehensive monitoring and observability stack manager"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.setup_kubernetes_client()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        
    def setup_kubernetes_client(self):
        """Initialize Kubernetes client"""
        try:
            config.load_kube_config()
        except Exception:
            config.load_incluster_config()
    
    def deploy_monitoring_stack(self) -> Dict[str, Any]:
        """Deploy complete monitoring stack"""
        logger.info("Deploying comprehensive monitoring stack...")
        
        results = {
            'namespace': self._create_monitoring_namespace(),
            'prometheus': self._deploy_prometheus(),
            'grafana': self._deploy_grafana(),
            'alertmanager': self._deploy_alertmanager(),
            'node_exporter': self._deploy_node_exporter(),
            'kube_state_metrics': self._deploy_kube_state_metrics(),
            'jaeger': self._deploy_jaeger_tracing(),
            'fluentd': self._deploy_log_aggregation(),
            'status': 'deployed'
        }
        
        logger.info("Monitoring stack deployment completed")
        return results
    
    def _create_monitoring_namespace(self) -> bool:
        """Create monitoring namespace"""
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=self.config.namespace,
                    labels={
                        'name': 'monitoring',
                        'managed-by': 'devops-agent'
                    }
                )
            )
            self.core_v1.create_namespace(body=namespace)
            logger.info(f"Created namespace: {self.config.namespace}")
            return True
        except client.ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"Namespace {self.config.namespace} already exists")
                return True
            logger.error(f"Failed to create namespace: {e}")
            return False
    
    def _deploy_prometheus(self) -> Dict[str, Any]:
        """Deploy Prometheus server with comprehensive configuration"""
        
        # Prometheus ConfigMap
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'alerting': {
                'alertmanagers': [
                    {
                        'static_configs': [
                            {'targets': ['alertmanager:9093']}
                        ]
                    }
                ]
            },
            'rule_files': [
                '/etc/prometheus/rules/*.yml'
            ],
            'scrape_configs': [
                {
                    'job_name': 'prometheus',
                    'static_configs': [
                        {'targets': ['localhost:9090']}
                    ]
                },
                {
                    'job_name': 'kubernetes-apiservers',
                    'kubernetes_sd_configs': [
                        {'role': 'endpoints'}
                    ],
                    'scheme': 'https',
                    'tls_config': {
                        'ca_file': '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
                    },
                    'bearer_token_file': '/var/run/secrets/kubernetes.io/serviceaccount/token',
                    'relabel_configs': [
                        {
                            'source_labels': ['__meta_kubernetes_namespace', '__meta_kubernetes_service_name', '__meta_kubernetes_endpoint_port_name'],
                            'action': 'keep',
                            'regex': 'default;kubernetes;https'
                        }
                    ]
                },
                {
                    'job_name': 'kubernetes-nodes',
                    'kubernetes_sd_configs': [
                        {'role': 'node'}
                    ],
                    'scheme': 'https',
                    'tls_config': {
                        'ca_file': '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
                    },
                    'bearer_token_file': '/var/run/secrets/kubernetes.io/serviceaccount/token',
                    'relabel_configs': [
                        {
                            'action': 'labelmap',
                            'regex': '__meta_kubernetes_node_label_(.+)'
                        }
                    ]
                },
                {
                    'job_name': 'kubernetes-pods',
                    'kubernetes_sd_configs': [
                        {'role': 'pod'}
                    ],
                    'relabel_configs': [
                        {
                            'source_labels': ['__meta_kubernetes_pod_annotation_prometheus_io_scrape'],
                            'action': 'keep',
                            'regex': 'true'
                        },
                        {
                            'source_labels': ['__meta_kubernetes_pod_annotation_prometheus_io_path'],
                            'action': 'replace',
                            'target_label': '__metrics_path__',
                            'regex': '(.+)'
                        },
                        {
                            'source_labels': ['__address__', '__meta_kubernetes_pod_annotation_prometheus_io_port'],
                            'action': 'replace',
                            'regex': '([^:]+)(?::\\d+)?;(\\d+)',
                            'replacement': '${1}:${2}',
                            'target_label': '__address__'
                        }
                    ]
                },
                {
                    'job_name': 'node-exporter',
                    'kubernetes_sd_configs': [
                        {'role': 'endpoints'}
                    ],
                    'relabel_configs': [
                        {
                            'source_labels': ['__meta_kubernetes_endpoints_name'],
                            'action': 'keep',
                            'regex': 'node-exporter'
                        }
                    ]
                },
                {
                    'job_name': 'kube-state-metrics',
                    'static_configs': [
                        {'targets': ['kube-state-metrics:8080']}
                    ]
                }
            ]
        }
        
        # Create ConfigMap
        prometheus_cm = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name="prometheus-config",
                namespace=self.config.namespace
            ),
            data={
                'prometheus.yml': yaml.dump(prometheus_config)
            }
        )
        
        try:
            self.core_v1.create_namespaced_config_map(
                namespace=self.config.namespace,
                body=prometheus_cm
            )
        except client.ApiException as e:
            if e.status != 409:
                raise
        
        # Prometheus Deployment
        prometheus_deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name="prometheus",
                namespace=self.config.namespace,
                labels={'app': 'prometheus'}
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={'app': 'prometheus'}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={'app': 'prometheus'}
                    ),
                    spec=client.V1PodSpec(
                        service_account_name="prometheus",
                        containers=[
                            client.V1Container(
                                name="prometheus",
                                image="prom/prometheus:v2.45.0",
                                ports=[
                                    client.V1ContainerPort(container_port=9090)
                                ],
                                args=[
                                    '--config.file=/etc/prometheus/prometheus.yml',
                                    '--storage.tsdb.path=/prometheus/',
                                    '--web.console.libraries=/etc/prometheus/console_libraries',
                                    '--web.console.templates=/etc/prometheus/consoles',
                                    '--storage.tsdb.retention.time=' + self.config.prometheus_retention,
                                    '--web.enable-lifecycle'
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="config-volume",
                                        mount_path="/etc/prometheus/"
                                    ),
                                    client.V1VolumeMount(
                                        name="storage-volume",
                                        mount_path="/prometheus/"
                                    )
                                ],
                                resources=client.V1ResourceRequirements(
                                    requests={'memory': '1Gi', 'cpu': '500m'},
                                    limits={'memory': '2Gi', 'cpu': '1000m'}
                                )
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="config-volume",
                                config_map=client.V1ConfigMapVolumeSource(
                                    name="prometheus-config"
                                )
                            ),
                            client.V1Volume(
                                name="storage-volume",
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name="prometheus-storage"
                                )
                            )
                        ]
                    )
                )
            )
        )
        
        # Create deployment
        self.apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=prometheus_deployment
        )
        
        # Create Service
        prometheus_service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name="prometheus",
                namespace=self.config.namespace,
                labels={'app': 'prometheus'}
            ),
            spec=client.V1ServiceSpec(
                selector={'app': 'prometheus'},
                ports=[
                    client.V1ServicePort(
                        port=9090,
                        target_port=9090,
                        protocol='TCP'
                    )
                ]
            )
        )
        
        self.core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=prometheus_service
        )
        
        return {'status': 'deployed', 'service': 'prometheus:9090'}
    
    def _deploy_grafana(self) -> Dict[str, Any]:
        """Deploy Grafana with pre-configured dashboards"""
        
        # Grafana ConfigMap for datasources
        grafana_datasources = {
            'apiVersion': 1,
            'datasources': [
                {
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'url': 'http://prometheus:9090',
                    'access': 'proxy',
                    'isDefault': True
                },
                {
                    'name': 'Jaeger',
                    'type': 'jaeger',
                    'url': 'http://jaeger-query:16686',
                    'access': 'proxy'
                }
            ]
        }
        
        grafana_datasources_cm = client.V1ConfigMap(
            metadata=client.V1ObjectMeta(
                name="grafana-datasources",
                namespace=self.config.namespace
            ),
            data={
                'datasources.yaml': yaml.dump(grafana_datasources)
            }
        )
        
        self.core_v1.create_namespaced_config_map(
            namespace=self.config.namespace,
            body=grafana_datasources_cm
        )
        
        # Grafana Deployment
        grafana_deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name="grafana",
                namespace=self.config.namespace,
                labels={'app': 'grafana'}
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(
                    match_labels={'app': 'grafana'}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={'app': 'grafana'}
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="grafana",
                                image="grafana/grafana:10.0.0",
                                ports=[
                                    client.V1ContainerPort(container_port=3000)
                                ],
                                env=[
                                    client.V1EnvVar(
                                        name="GF_SECURITY_ADMIN_PASSWORD",
                                        value=self.config.grafana_admin_password
                                    ),
                                    client.V1EnvVar(
                                        name="GF_INSTALL_PLUGINS",
                                        value="grafana-kubernetes-app"
                                    )
                                ],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="datasources",
                                        mount_path="/etc/grafana/provisioning/datasources"
                                    ),
                                    client.V1VolumeMount(
                                        name="storage",
                                        mount_path="/var/lib/grafana"
                                    )
                                ],
                                resources=client.V1ResourceRequirements(
                                    requests={'memory': '512Mi', 'cpu': '250m'},
                                    limits={'memory': '1Gi', 'cpu': '500m'}
                                )
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="datasources",
                                config_map=client.V1ConfigMapVolumeSource(
                                    name="grafana-datasources"
                                )
                            ),
                            client.V1Volume(
                                name="storage",
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name="grafana-storage"
                                )
                            )
                        ]
                    )
                )
            )
        )
        
        self.apps_v1.create_namespaced_deployment(
            namespace=self.config.namespace,
            body=grafana_deployment
        )
        
        # Create Service
        grafana_service = client.V1Service(
            metadata=client.V1ObjectMeta(
                name="grafana",
                namespace=self.config.namespace,
                labels={'app': 'grafana'}
            ),
            spec=client.V1ServiceSpec(
                selector={'app': 'grafana'},
                ports=[
                    client.V1ServicePort(
                        port=3000,
                        target_port=3000,
                        protocol='TCP'
                    )
                ]
            )
        )
        
        self.core_v1.create_namespaced_service(
            namespace=self.config.namespace,
            body=grafana_service
        )
        
        return {'status': 'deployed', 'service': 'grafana:3000'}
    
    def create_custom_dashboards(self) -> List[Dict[str, Any]]:
        """Create custom Grafana dashboards for application monitoring"""
        
        dashboards = [
            {
                'name': 'Kubernetes Cluster Overview',
                'panels': [
                    'Cluster CPU Usage',
                    'Cluster Memory Usage',
                    'Node Status',
                    'Pod Status',
                    'Deployment Status'
                ]
            },
            {
                'name': 'Application Performance',
                'panels': [
                    'Request Rate',
                    'Response Time',
                    'Error Rate',
                    'Database Connections',
                    'Cache Hit Rate'
                ]
            },
            {
                'name': 'Infrastructure Metrics',
                'panels': [
                    'Disk Usage',
                    'Network I/O',
                    'Load Balancer Metrics',
                    'Database Performance',
                    'Redis Performance'
                ]
            }
        ]
        
        logger.info(f"Created {len(dashboards)} custom dashboards")
        return dashboards

def setup_alerting_rules() -> Dict[str, Any]:
    """Setup comprehensive alerting rules"""
    
    alerting_rules = {
        'groups': [
            {
                'name': 'kubernetes.rules',
                'rules': [
                    {
                        'alert': 'KubernetesPodCrashLooping',
                        'expr': 'rate(kube_pod_container_status_restarts_total[5m]) * 60 * 5 > 0',
                        'for': '0m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'Pod {{ $labels.pod }} is crash looping',
                            'description': 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is restarting frequently'
                        }
                    },
                    {
                        'alert': 'KubernetesNodeNotReady',
                        'expr': 'kube_node_status_condition{condition="Ready",status="true"} == 0',
                        'for': '10m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': 'Kubernetes node {{ $labels.node }} is not ready',
                            'description': 'Node {{ $labels.node }} has been unready for more than 10 minutes'
                        }
                    },
                    {
                        'alert': 'KubernetesPodNotReady',
                        'expr': 'kube_pod_status_ready{condition="true"} == 0',
                        'for': '15m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'Pod {{ $labels.pod }} not ready',
                            'description': 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has been in a non-ready state for longer than 15 minutes'
                        }
                    }
                ]
            },
            {
                'name': 'application.rules',
                'rules': [
                    {
                        'alert': 'HighErrorRate',
                        'expr': 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5',
                        'for': '10m',
                        'labels': {
                            'severity': 'critical'
                        },
                        'annotations': {
                            'summary': 'High error rate detected',
                            'description': 'Error rate is {{ $value }}% for {{ $labels.job }}'
                        }
                    },
                    {
                        'alert': 'HighResponseTime',
                        'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1',
                        'for': '10m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'High response time detected',
                            'description': '95th percentile response time is {{ $value }}s for {{ $labels.job }}'
                        }
                    },
                    {
                        'alert': 'DatabaseConnectionHigh',
                        'expr': 'pg_stat_activity_count / pg_settings_max_connections * 100 > 80',
                        'for': '5m',
                        'labels': {
                            'severity': 'warning'
                        },
                        'annotations': {
                            'summary': 'Database connection usage high',
                            'description': 'Database connection usage is {{ $value }}%'
                        }
                    }
                ]
            }
        ]
    }
    
    return alerting_rules

def main():
    """Main function to deploy monitoring stack"""
    monitoring_config = MonitoringConfig(
        cluster_name="production-cluster",
        namespace="monitoring",
        prometheus_retention="30d",
        grafana_admin_password="secure-password-123"
    )
    
    manager = MonitoringStackManager(monitoring_config)
    
    # Deploy monitoring stack
    results = manager.deploy_monitoring_stack()
    
    # Create custom dashboards
    dashboards = manager.create_custom_dashboards()
    
    # Setup alerting rules
    alerts = setup_alerting_rules()
    
    logger.info("Monitoring stack deployment completed successfully")
    logger.info(f"Results: {json.dumps(results, indent=2)}")

if __name__ == "__main__":
    main()
```

### 5. GitOps Workflow Implementation
```bash
#!/bin/bash
# gitops-deployment.sh - Comprehensive GitOps deployment automation

set -euo pipefail

# Configuration
ENVIRONMENT="${ENVIRONMENT:-staging}"
CLUSTER_NAME="${CLUSTER_NAME:-webapp-${ENVIRONMENT}-eks}"
AWS_REGION="${AWS_REGION:-us-west-2}"
ARGOCD_NAMESPACE="${ARGOCD_NAMESPACE:-argocd}"
APP_NAMESPACE="${APP_NAMESPACE:-${ENVIRONMENT}}"
REPO_URL="${REPO_URL:-https://github.com/company/webapp-gitops}"
ARGOCD_VERSION="${ARGOCD_VERSION:-v2.8.0}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local required_tools=("kubectl" "helm" "aws" "git" "yq" "curl")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install missing tools and try again"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or expired"
        exit 1
    fi
    
    # Check kubectl context
    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl not configured or cluster unreachable"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Setup ArgoCD
setup_argocd() {
    log_info "Setting up ArgoCD..."
    
    # Create namespace
    kubectl create namespace "$ARGOCD_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    # Install ArgoCD
    kubectl apply -n "$ARGOCD_NAMESPACE" -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"
    
    # Wait for ArgoCD to be ready
    log_info "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n "$ARGOCD_NAMESPACE"
    
    # Patch ArgoCD server service to LoadBalancer (optional)
    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl patch svc argocd-server -n "$ARGOCD_NAMESPACE" -p '{"spec": {"type": "LoadBalancer"}}'
    fi
    
    # Get ArgoCD admin password
    local argocd_password
    argocd_password=$(kubectl -n "$ARGOCD_NAMESPACE" get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    
    log_success "ArgoCD installed successfully"
    log_info "ArgoCD admin password: $argocd_password"
    
    # Setup ArgoCD CLI (if needed)
    setup_argocd_cli "$argocd_password"
}

# Setup ArgoCD CLI
setup_argocd_cli() {
    local admin_password="$1"
    
    log_info "Setting up ArgoCD CLI..."
    
    # Download ArgoCD CLI if not present
    if ! command -v argocd &> /dev/null; then
        log_info "Downloading ArgoCD CLI..."
        curl -sSL -o /tmp/argocd "https://github.com/argoproj/argo-cd/releases/download/${ARGOCD_VERSION}/argocd-linux-amd64"
        chmod +x /tmp/argocd
        sudo mv /tmp/argocd /usr/local/bin/argocd
    fi
    
    # Port forward to ArgoCD server
    kubectl port-forward svc/argocd-server -n "$ARGOCD_NAMESPACE" 8080:443 &
    local port_forward_pid=$!
    
    sleep 5
    
    # Login to ArgoCD
    argocd login localhost:8080 --username admin --password "$admin_password" --insecure
    
    # Kill port forward
    kill $port_forward_pid 2>/dev/null || true
    
    log_success "ArgoCD CLI configured"
}

# Create ArgoCD Application
create_argocd_application() {
    log_info "Creating ArgoCD application..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: webapp-${ENVIRONMENT}
  namespace: ${ARGOCD_NAMESPACE}
  labels:
    environment: ${ENVIRONMENT}
    managed-by: devops-agent
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: ${REPO_URL}
    targetRevision: HEAD
    path: manifests/${ENVIRONMENT}
    helm:
      valueFiles:
        - values.yaml
        - values-${ENVIRONMENT}.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: ${APP_NAMESPACE}
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  revisionHistoryLimit: 10
EOF

    log_success "ArgoCD application created"
}

# Create GitOps repository structure
create_gitops_structure() {
    log_info "Creating GitOps repository structure..."
    
    local temp_dir="/tmp/gitops-setup"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    cd "$temp_dir"
    
    # Clone or create repository
    if git clone "$REPO_URL" gitops-repo 2>/dev/null; then
        cd gitops-repo
        log_info "Using existing repository"
    else
        mkdir gitops-repo
        cd gitops-repo
        git init
        log_info "Created new repository structure"
    fi
    
    # Create directory structure
    mkdir -p "manifests/${ENVIRONMENT}"
    mkdir -p "helm-charts/webapp"
    mkdir -p "environments/${ENVIRONMENT}"
    
    # Create base Helm chart
    create_helm_chart
    
    # Create environment-specific values
    create_environment_values
    
    # Create Kubernetes manifests
    create_kubernetes_manifests
    
    # Commit changes
    git add .
    git commit -m "Initial GitOps setup for ${ENVIRONMENT}" || true
    
    log_success "GitOps repository structure created"
    
    cd - > /dev/null
    rm -rf "$temp_dir"
}

# Create Helm chart
create_helm_chart() {
    log_info "Creating Helm chart..."
    
    # Chart.yaml
    cat <<EOF > helm-charts/webapp/Chart.yaml
apiVersion: v2
name: webapp
description: Web application Helm chart
type: application
version: 0.1.0
appVersion: "1.0"
dependencies:
  - name: postgresql
    version: 12.8.2
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: 17.11.3
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
EOF

    # values.yaml
    cat <<EOF > helm-charts/webapp/values.yaml
replicaCount: 2

image:
  repository: ghcr.io/company/webapp
  pullPolicy: IfNotPresent
  tag: "latest"

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"

podSecurityContext:
  fsGroup: 2000
  runAsNonRoot: true
  runAsUser: 1000

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: webapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: webapp-tls
      hosts:
        - webapp.example.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}

postgresql:
  enabled: true
  auth:
    postgresPassword: "changeme"
    database: "webapp"
  primary:
    persistence:
      enabled: true
      size: 10Gi

redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 8Gi

env:
  DATABASE_URL: "postgresql://postgres:changeme@webapp-postgresql:5432/webapp"
  REDIS_URL: "redis://webapp-redis-master:6379"
  NODE_ENV: "production"

healthCheck:
  enabled: true
  livenessProbe:
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30
    periodSeconds: 10
  readinessProbe:
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 5
EOF
}

# Create environment-specific values
create_environment_values() {
    log_info "Creating environment-specific values..."
    
    case "$ENVIRONMENT" in
        "development")
            cat <<EOF > "manifests/${ENVIRONMENT}/values-${ENVIRONMENT}.yaml"
replicaCount: 1

image:
  tag: "develop"

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false

postgresql:
  primary:
    persistence:
      size: 5Gi

redis:
  master:
    persistence:
      size: 2Gi

ingress:
  enabled: true
  hosts:
    - host: webapp-dev.example.com
      paths:
        - path: /
          pathType: Prefix
EOF
            ;;
        "staging")
            cat <<EOF > "manifests/${ENVIRONMENT}/values-${ENVIRONMENT}.yaml"
replicaCount: 2

image:
  tag: "staging"

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5

postgresql:
  primary:
    persistence:
      size: 20Gi

redis:
  master:
    persistence:
      size: 5Gi

ingress:
  enabled: true
  hosts:
    - host: webapp-staging.example.com
      paths:
        - path: /
          pathType: Prefix
EOF
            ;;
        "production")
            cat <<EOF > "manifests/${ENVIRONMENT}/values-${ENVIRONMENT}.yaml"
replicaCount: 3

image:
  tag: "v1.0.0"

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20

postgresql:
  enabled: false  # Use external RDS

redis:
  enabled: false  # Use external ElastiCache

env:
  DATABASE_URL: "postgresql://user:pass@prod-db.cluster-xyz.us-west-2.rds.amazonaws.com:5432/webapp"
  REDIS_URL: "redis://prod-cache.abc123.cache.amazonaws.com:6379"

ingress:
  enabled: true
  hosts:
    - host: webapp.example.com
      paths:
        - path: /
          pathType: Prefix

podDisruptionBudget:
  enabled: true
  minAvailable: 2
EOF
            ;;
    esac
}

# Create Kubernetes manifests
create_kubernetes_manifests() {
    log_info "Creating Kubernetes manifests..."
    
    # Application manifest that references Helm chart
    cat <<EOF > "manifests/${ENVIRONMENT}/application.yaml"
apiVersion: v1
kind: Namespace
metadata:
  name: ${APP_NAMESPACE}
  labels:
    environment: ${ENVIRONMENT}
    managed-by: argocd
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: ${APP_NAMESPACE}
data:
  app.properties: |
    server.port=8080
    logging.level.root=INFO
    spring.profiles.active=${ENVIRONMENT}
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: ${APP_NAMESPACE}
type: Opaque
stringData:
  jwt-secret: "super-secret-jwt-key"
  api-key: "api-key-placeholder"
EOF

    # NetworkPolicy for security
    cat <<EOF > "manifests/${ENVIRONMENT}/network-policy.yaml"
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: webapp-network-policy
  namespace: ${APP_NAMESPACE}
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: webapp
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: webapp
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: postgresql
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
EOF
}

# Deploy with ArgoCD
deploy_with_argocd() {
    log_info "Deploying application with ArgoCD..."
    
    # Sync the application
    if command -v argocd &> /dev/null; then
        argocd app sync "webapp-${ENVIRONMENT}" --prune
        argocd app wait "webapp-${ENVIRONMENT}" --timeout 600
    else
        log_warning "ArgoCD CLI not available, manual sync required"
    fi
    
    # Check deployment status
    kubectl rollout status deployment/webapp -n "$APP_NAMESPACE" --timeout=300s
    
    log_success "Application deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check if pods are running
    local ready_pods
    ready_pods=$(kubectl get pods -n "$APP_NAMESPACE" -l app.kubernetes.io/name=webapp --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$ready_pods" -gt 0 ]; then
        log_success "Application pods are running ($ready_pods pods)"
    else
        log_error "No application pods running"
        return 1
    fi
    
    # Check service endpoint
    local service_ip
    service_ip=$(kubectl get svc webapp -n "$APP_NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    
    if [ -n "$service_ip" ]; then
        log_success "Service accessible at $service_ip"
    else
        log_error "Service not accessible"
        return 1
    fi
    
    log_success "Health check passed"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary resources..."
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
}

# Main deployment function
main() {
    log_info "Starting GitOps deployment for environment: $ENVIRONMENT"
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    setup_argocd
    create_gitops_structure
    create_argocd_application
    deploy_with_argocd
    health_check
    
    log_success "GitOps deployment completed successfully!"
    log_info "Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    log_info "Application namespace: $APP_NAMESPACE"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Operational Workflows

### 1. Production Deployment Workflow
**Trigger**: Release tag creation or manual production deployment
**Steps**:
1. Security scan validation and approval gate
2. Infrastructure provisioning/validation with Terraform
3. Blue-green deployment strategy execution
4. Automated testing suite (smoke, integration, load tests)
5. Gradual traffic migration with monitoring
6. Rollback automation on failure detection
7. Post-deployment verification and notifications

### 2. Infrastructure Scaling Workflow
**Trigger**: Resource utilization thresholds or manual scaling request
**Steps**:
1. Resource requirement analysis and capacity planning
2. Auto-scaling configuration updates (HPA, VPA, Cluster Autoscaler)
3. Infrastructure cost impact assessment
4. Gradual scaling with performance monitoring
5. Optimization recommendations based on usage patterns

### 3. Disaster Recovery Workflow
**Trigger**: Infrastructure failure or disaster recovery drill
**Steps**:
1. Automated backup verification and integrity checks
2. Multi-region failover coordination
3. Database and state recovery procedures
4. Service mesh and load balancer reconfiguration
5. End-to-end system validation
6. Stakeholder communication and status updates

### 4. Security Compliance Workflow
**Trigger**: Security audit requirements or vulnerability detection
**Steps**:
1. Comprehensive security scanning (SAST, DAST, container scanning)
2. Infrastructure compliance validation (CIS benchmarks)
3. Access control and permission auditing
4. Encryption and secret management verification
5. Compliance report generation and remediation tracking

### 5. Performance Optimization Workflow
**Trigger**: Performance degradation alerts or optimization requests
**Steps**:
1. Comprehensive performance profiling and bottleneck identification
2. Resource optimization recommendations (CPU, memory, storage)
3. Database query optimization and index analysis
4. Caching strategy evaluation and optimization
5. CDN and edge performance optimization
6. Application-level performance tuning recommendations

### 6. Monitoring and Alerting Workflow
**Trigger**: Service health degradation or threshold breaches
**Steps**:
1. Multi-layered health check execution (application, infrastructure, database)
2. Alert correlation and noise reduction
3. Automated remediation for known issues
4. Escalation path management
5. Incident documentation and post-mortem analysis

### 7. Cost Optimization Workflow
**Trigger**: Budget threshold alerts or cost optimization requests
**Steps**:
1. Resource utilization analysis and rightsizing recommendations
2. Reserved instance and spot instance optimization
3. Storage optimization and lifecycle management
4. Network cost analysis and optimization
5. Cost allocation and chargeback reporting

## Tool Utilization Patterns

### Terraform Integration
- **Infrastructure State Management**: Centralized state storage with S3 and DynamoDB locking
- **Multi-Environment Support**: Environment-specific variable files and workspace management
- **Module Development**: Reusable infrastructure components for consistency
- **Drift Detection**: Regular state validation and reconciliation
- **Cost Estimation**: Integration with terraform-cost-estimation tools

### Kubernetes Orchestration
- **Cluster Management**: Multi-cluster deployment and management strategies
- **Resource Optimization**: Intelligent resource allocation and scaling policies
- **Security Hardening**: Pod security policies, network policies, and RBAC implementation
- **Workload Distribution**: Multi-zone deployment and anti-affinity rules
- **Storage Management**: Persistent volume management and backup strategies

### CI/CD Pipeline Integration
- **Multi-Stage Deployments**: Environment-specific deployment pipelines
- **Quality Gates**: Automated testing, security scanning, and approval processes
- **Artifact Management**: Container image scanning, signing, and promotion
- **Deployment Strategies**: Blue-green, canary, and rolling update implementations
- **Rollback Automation**: Automated failure detection and rollback procedures

### Monitoring and Observability
- **Metrics Collection**: Comprehensive application and infrastructure metrics
- **Log Aggregation**: Centralized logging with structured log analysis
- **Distributed Tracing**: End-to-end request tracing and performance analysis
- **Alerting Intelligence**: Smart alerting with correlation and noise reduction
- **Dashboard Automation**: Auto-generated dashboards based on service discovery

## Advanced Features

### 1. Intelligent Resource Allocation System
```python
def intelligent_resource_allocation(workload_profile: Dict[str, Any], 
                                  historical_data: List[Dict[str, Any]],
                                  cost_constraints: Dict[str, float]) -> Dict[str, Any]:
    """
    Machine learning-powered resource allocation optimization
    """
    # Analyze historical resource usage patterns
    usage_patterns = analyze_usage_patterns(historical_data)
    
    # Predict future resource requirements
    predicted_requirements = predict_resource_needs(workload_profile, usage_patterns)
    
    # Optimize for cost and performance
    optimized_allocation = optimize_allocation(
        predicted_requirements, 
        cost_constraints,
        performance_requirements=workload_profile.get('performance_sla')
    )
    
    # Generate auto-scaling policies
    scaling_policies = generate_scaling_policies(optimized_allocation, usage_patterns)
    
    return {
        'recommended_resources': optimized_allocation,
        'scaling_policies': scaling_policies,
        'cost_projection': calculate_cost_projection(optimized_allocation),
        'performance_expectations': generate_performance_expectations(optimized_allocation)
    }
```

### 2. Multi-Cloud Deployment Orchestration
```python
def multi_cloud_deployment_strategy(application_config: Dict[str, Any],
                                  cloud_preferences: List[str],
                                  disaster_recovery_requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrate deployments across multiple cloud providers
    """
    deployment_plan = {
        'primary_cloud': determine_primary_cloud(cloud_preferences, application_config),
        'secondary_clouds': select_secondary_clouds(cloud_preferences, disaster_recovery_requirements),
        'data_replication_strategy': design_data_replication(disaster_recovery_requirements),
        'traffic_distribution': calculate_traffic_distribution(cloud_preferences),
        'failover_procedures': generate_failover_procedures(disaster_recovery_requirements)
    }
    
    # Generate cloud-specific configurations
    for cloud in deployment_plan['primary_cloud'] + deployment_plan['secondary_clouds']:
        deployment_plan[f'{cloud}_config'] = generate_cloud_config(
            cloud, application_config, deployment_plan
        )
    
    return deployment_plan
```

### 3. Automated Compliance and Security Hardening
```python
def automated_security_hardening(infrastructure_config: Dict[str, Any],
                               compliance_frameworks: List[str],
                               security_policies: Dict[str, Any]) -> Dict[str, Any]:
    """
    Automatically apply security hardening and compliance measures
    """
    hardening_results = {
        'security_configurations': [],
        'compliance_validations': [],
        'remediation_actions': [],
        'monitoring_enhancements': []
    }
    
    # Apply security hardening based on frameworks
    for framework in compliance_frameworks:
        framework_config = apply_security_framework(framework, infrastructure_config)
        hardening_results['security_configurations'].append(framework_config)
    
    # Generate monitoring and alerting rules
    security_monitoring = generate_security_monitoring(security_policies)
    hardening_results['monitoring_enhancements'].extend(security_monitoring)
    
    # Create automated remediation procedures
    remediation_procedures = create_remediation_procedures(security_policies)
    hardening_results['remediation_actions'].extend(remediation_procedures)
    
    return hardening_results
```

### 4. Predictive Infrastructure Scaling
```python
def predictive_scaling_engine(metrics_history: List[Dict[str, Any]],
                            traffic_patterns: Dict[str, Any],
                            business_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Predict infrastructure scaling needs based on multiple data sources
    """
    # Analyze historical scaling patterns
    scaling_patterns = analyze_scaling_history(metrics_history)
    
    # Incorporate business event impact
    event_impact = calculate_business_event_impact(business_events, scaling_patterns)
    
    # Generate predictive scaling recommendations
    scaling_predictions = generate_scaling_predictions(
        scaling_patterns,
        traffic_patterns,
        event_impact
    )
    
    # Create proactive scaling policies
    proactive_policies = create_proactive_scaling_policies(scaling_predictions)
    
    return {
        'scaling_predictions': scaling_predictions,
        'recommended_policies': proactive_policies,
        'cost_impact': calculate_scaling_cost_impact(scaling_predictions),
        'confidence_intervals': calculate_prediction_confidence(scaling_predictions)
    }
```

## Quality Assurance Checklists

### Infrastructure Deployment Checklist
- [ ] Terraform state validation and backup verification
- [ ] Resource tagging compliance and cost allocation
- [ ] Security group and network ACL validation
- [ ] Encryption at rest and in transit verification
- [ ] Backup and disaster recovery testing
- [ ] Performance baseline establishment
- [ ] Monitoring and alerting configuration
- [ ] Documentation and runbook updates

### Container Orchestration Checklist
- [ ] Container image vulnerability scanning results
- [ ] Resource limits and requests configuration
- [ ] Health check and readiness probe validation
- [ ] Service mesh configuration and security policies
- [ ] Persistent volume backup and recovery testing
- [ ] Network policy and ingress configuration
- [ ] RBAC and service account permissions
- [ ] Pod disruption budget and anti-affinity rules

### CI/CD Pipeline Checklist
- [ ] Pipeline security and secret management
- [ ] Automated testing coverage and quality gates
- [ ] Deployment strategy validation and rollback testing
- [ ] Environment parity and configuration management
- [ ] Artifact signing and vulnerability scanning
- [ ] Performance and load testing integration
- [ ] Monitoring and observability integration
- [ ] Compliance and audit trail maintenance

### Security and Compliance Checklist
- [ ] Access control and permission auditing
- [ ] Encryption key management and rotation
- [ ] Network security and segmentation validation
- [ ] Vulnerability scanning and remediation tracking
- [ ] Compliance framework adherence verification
- [ ] Incident response procedure testing
- [ ] Security monitoring and alerting validation
- [ ] Third-party security assessment compliance

## Integration Specifications

### Backend Services Integration
- **API Gateway Configuration**: Intelligent routing, rate limiting, and authentication
- **Service Discovery**: Automated service registration and health checking
- **Load Balancing**: Advanced load balancing strategies with health-based routing
- **Circuit Breaker**: Resilience patterns for service communication

### Database Architecture Integration
- **Database Deployment**: Automated database provisioning and configuration
- **Backup and Recovery**: Comprehensive backup strategies and disaster recovery
- **Performance Monitoring**: Database performance optimization and alerting
- **Schema Management**: Database migration and versioning automation

### Security Architecture Integration
- **Secret Management**: Automated secret rotation and secure distribution
- **Certificate Management**: TLS certificate automation and renewal
- **Access Control**: RBAC implementation and policy enforcement
- **Audit Logging**: Comprehensive audit trail and compliance reporting

### Performance Optimization Integration
- **Auto-scaling**: Intelligent scaling based on multiple metrics
- **Caching Strategy**: Multi-layer caching implementation and optimization
- **CDN Integration**: Content delivery optimization and edge caching
- **Database Optimization**: Query optimization and index management

## Error Handling and Recovery

### Infrastructure Failures
- **Automated Detection**: Multi-layered health checking and failure detection
- **Self-Healing**: Automated recovery procedures for common failure scenarios
- **Escalation Procedures**: Intelligent escalation based on failure severity and impact
- **Communication**: Automated stakeholder notification and status updates

### Deployment Failures
- **Rollback Automation**: Intelligent rollback triggers and procedures
- **Partial Failure Handling**: Graceful degradation and service isolation
- **Data Consistency**: Transaction rollback and data integrity verification
- **Root Cause Analysis**: Automated failure analysis and improvement recommendations

### Performance Degradation
- **Threshold-Based Scaling**: Automated scaling based on performance metrics
- **Resource Optimization**: Dynamic resource allocation and optimization
- **Traffic Management**: Intelligent traffic routing and load distribution
- **Capacity Planning**: Proactive capacity management and planning

### Security Incidents
- **Incident Response**: Automated security incident detection and response
- **Isolation Procedures**: Automated threat isolation and containment
- **Forensic Analysis**: Comprehensive incident analysis and documentation
- **Recovery Procedures**: Systematic recovery and hardening procedures

## Performance Guidelines

### Infrastructure Performance
- **Deployment Speed**: Target deployment time under 10 minutes for standard applications
- **Scalability**: Support for 10x traffic scaling with automated resource management
- **Availability**: 99.9% uptime target with automated failover procedures
- **Recovery Time**: RTO of 15 minutes and RPO of 5 minutes for critical systems

### Resource Optimization
- **CPU Utilization**: Target 70-80% CPU utilization with proper headroom
- **Memory Efficiency**: Optimized memory allocation with minimal waste
- **Storage Performance**: High IOPS storage with automated tiering
- **Network Optimization**: Optimized network routing and bandwidth utilization

### Cost Optimization
- **Resource Rightsizing**: Continuous rightsizing based on actual usage
- **Reserved Instance Optimization**: Optimal reserved instance purchasing strategies
- **Spot Instance Utilization**: Intelligent spot instance usage for cost savings
- **Storage Optimization**: Automated storage lifecycle management

### Monitoring Performance
- **Metric Collection**: Sub-second metric collection and aggregation
- **Alert Response**: Alert processing and notification within 30 seconds
- **Dashboard Load Time**: Dashboard load times under 2 seconds
- **Data Retention**: Optimized data retention with automated archiving

## Command Reference

### Infrastructure Management Commands
```bash
# Deploy infrastructure for specific environment
devops-agent deploy-infrastructure --environment production --validate-plan

# Scale cluster nodes
devops-agent scale-cluster --min-nodes 3 --max-nodes 20 --desired-nodes 5

# Update infrastructure configuration
devops-agent update-infrastructure --config-file infrastructure.yaml --dry-run

# Validate infrastructure state
devops-agent validate-infrastructure --check-drift --generate-report

# Backup infrastructure state
devops-agent backup-state --destination s3://backup-bucket/terraform-state

# Generate cost report
devops-agent cost-analysis --timeframe 30d --breakdown-by-service

# Security scan infrastructure
devops-agent security-scan --compliance-framework SOC2 --generate-report

# Disaster recovery test
devops-agent test-disaster-recovery --scenario region-failure --validate-rto-rpo
```

### Container Orchestration Commands
```bash
# Deploy application with advanced configuration
devops-agent deploy-app --config deployment.yaml --strategy blue-green --health-check-timeout 300

# Scale application deployment
devops-agent scale-app --deployment webapp --replicas 5 --namespace production

# Update application image
devops-agent update-image --deployment webapp --image webapp:v1.2.3 --rollback-on-failure

# Validate cluster health
devops-agent cluster-health --deep-check --generate-report

# Manage secrets and configurations
devops-agent manage-secrets --action rotate --secret-name database-password

# Network policy validation
devops-agent validate-network-policies --namespace production --test-connectivity

# Resource optimization analysis
devops-agent optimize-resources --analyze-usage --recommend-sizing

# Certificate management
devops-agent manage-certificates --action renew --namespace production
```

### Monitoring and Alerting Commands
```bash
# Deploy monitoring stack
devops-agent deploy-monitoring --stack-config monitoring.yaml --enable-alerting

# Configure custom dashboards
devops-agent setup-dashboards --template application-metrics --customize-for webapp

# Test alerting rules
devops-agent test-alerts --rule-file alert-rules.yaml --simulate-conditions

# Generate SLI/SLO reports
devops-agent slo-report --service webapp --timeframe 7d --format pdf

# Performance analysis
devops-agent analyze-performance --service webapp --identify-bottlenecks

# Log analysis and insights
devops-agent analyze-logs --pattern error --timeframe 24h --generate-insights

# Trace analysis
devops-agent trace-analysis --service webapp --slow-requests --optimize-paths

# Capacity planning
devops-agent capacity-planning --service webapp --predict-growth --timeframe 90d
```

### CI/CD Pipeline Commands
```bash
# Setup CI/CD pipeline
devops-agent setup-pipeline --repo-url https://github.com/company/webapp --template production

# Validate pipeline configuration
devops-agent validate-pipeline --config .github/workflows/ci-cd.yml --security-check

# Execute deployment pipeline
devops-agent run-pipeline --stage production --approval-required --notify-teams

# Rollback deployment
devops-agent rollback --deployment webapp --to-version v1.2.2 --verify-health

# Pipeline optimization analysis
devops-agent optimize-pipeline --analyze-bottlenecks --recommend-improvements

# Security scanning integration
devops-agent integrate-security-scanning --tools trivy,sonarcloud --fail-on-critical

# Performance testing integration
devops-agent setup-performance-testing --tool k6 --baseline-metrics --regression-detection

# Compliance validation
devops-agent validate-compliance --framework SOC2 --generate-evidence
```

### GitOps Management Commands
```bash
# Initialize GitOps repository
devops-agent init-gitops --repo-url https://github.com/company/gitops --structure-template standard

# Deploy ArgoCD
devops-agent deploy-argocd --cluster-name production --enable-sso --backup-config

# Sync applications
devops-agent sync-apps --application webapp-production --prune --health-check

# Validate GitOps configuration
devops-agent validate-gitops --check-security --validate-manifests --generate-report

# GitOps drift detection
devops-agent detect-drift --application webapp-production --auto-remediate

# Promote across environments
devops-agent promote --application webapp --from staging --to production --approval-required

# Backup GitOps state
devops-agent backup-gitops --destination s3://gitops-backup --include-secrets

# GitOps security scanning
devops-agent scan-gitops --check-manifests --validate-rbac --security-policies
```

### Troubleshooting Commands
```bash
# Comprehensive health check
devops-agent health-check --deep-analysis --include-dependencies --generate-report

# Debug deployment issues
devops-agent debug-deployment --deployment webapp --analyze-logs --check-resources

# Network connectivity testing
devops-agent test-connectivity --source webapp --destination database --protocol tcp

# Resource utilization analysis
devops-agent analyze-resources --namespace production --identify-hotspots --recommend-actions

# Performance profiling
devops-agent profile-performance --service webapp --duration 300s --include-traces

# Security incident response
devops-agent incident-response --type security --isolate-affected --collect-evidence

# Disaster recovery validation
devops-agent validate-dr --scenario database-failure --test-procedures --measure-rto

# Configuration drift analysis
devops-agent analyze-drift --baseline infrastructure-baseline.yaml --generate-remediation
```

This comprehensive DevOps Engineering Agent provides extensive capabilities for infrastructure automation, container orchestration, CI/CD pipeline management, monitoring, and operational excellence. The agent integrates seamlessly with modern DevOps toolchains and provides intelligent automation for complex deployment scenarios while maintaining security, compliance, and performance standards.