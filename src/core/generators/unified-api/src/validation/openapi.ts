/**
 * OpenAPI specification validation for the Unified MCP Generator
 */

import SwaggerParser from '@apidevtools/swagger-parser';
import { OpenAPIV3 } from 'openapi-types';
import { ValidationResult } from '../types.js';

/**
 * Validates an OpenAPI specification
 */
export async function validateOpenAPISpec(
  specPath: string,
  options: {
    strict?: boolean;
    dereference?: boolean;
  } = {}
): Promise<{
  validation: ValidationResult;
  spec?: OpenAPIV3.Document;
}> {
  const errors: ValidationResult['errors'] = [];
  const warnings: ValidationResult['warnings'] = [];

  try {
    // Parse and validate the OpenAPI spec
    const api = options.dereference
      ? await SwaggerParser.dereference(specPath)
      : await SwaggerParser.parse(specPath);

    const spec = api as OpenAPIV3.Document;

    // Additional custom validations
    await performCustomValidations(spec, { errors, warnings, strict: options.strict });

    return {
      validation: {
        valid: errors.length === 0,
        errors,
        warnings
      },
      spec
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown validation error';
    
    errors.push({
      path: 'root',
      message: `OpenAPI validation failed: ${errorMessage}`,
      code: 'openapi_validation_error',
      severity: 'error'
    });

    return {
      validation: {
        valid: false,
        errors,
        warnings
      }
    };
  }
}

/**
 * Performs custom validations on the OpenAPI specification
 */
async function performCustomValidations(
  spec: OpenAPIV3.Document,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
    strict?: boolean;
  }
): Promise<void> {
  const { errors, warnings, strict } = context;

  // Check OpenAPI version
  if (!spec.openapi || !spec.openapi.startsWith('3.')) {
    errors.push({
      path: 'openapi',
      message: 'Only OpenAPI 3.x specifications are supported',
      code: 'unsupported_openapi_version',
      severity: 'error'
    });
  }

  // Check for required info section
  if (!spec.info) {
    errors.push({
      path: 'info',
      message: 'OpenAPI specification must include an info section',
      code: 'missing_info_section',
      severity: 'error'
    });
  } else {
    // Check info fields
    if (!spec.info.title) {
      warnings.push({
        path: 'info.title',
        message: 'API title is missing - will use default name',
        code: 'missing_title'
      });
    }

    if (!spec.info.version) {
      warnings.push({
        path: 'info.version',
        message: 'API version is missing - will use default version',
        code: 'missing_version'
      });
    }

    if (!spec.info.description) {
      warnings.push({
        path: 'info.description',
        message: 'API description is missing',
        code: 'missing_description'
      });
    }
  }

  // Check for servers
  if (!spec.servers || spec.servers.length === 0) {
    warnings.push({
      path: 'servers',
      message: 'No servers defined - base URL must be provided via configuration',
      code: 'missing_servers'
    });
  } else {
    // Validate server URLs
    spec.servers.forEach((server, index) => {
      if (!server.url) {
        errors.push({
          path: `servers[${index}].url`,
          message: 'Server URL is required',
          code: 'missing_server_url',
          severity: 'error'
        });
      } else {
        try {
          new URL(server.url.includes('://') ? server.url : `https://${server.url}`);
        } catch {
          warnings.push({
            path: `servers[${index}].url`,
            message: `Server URL "${server.url}" may be invalid`,
            code: 'invalid_server_url'
          });
        }
      }
    });
  }

  // Check for paths
  if (!spec.paths || Object.keys(spec.paths).length === 0) {
    errors.push({
      path: 'paths',
      message: 'OpenAPI specification must include at least one path',
      code: 'missing_paths',
      severity: 'error'
    });
  } else {
    await validatePaths(spec.paths, { errors, warnings, strict });
  }

  // Check for components
  if (spec.components) {
    await validateComponents(spec.components, { errors, warnings, strict });
  }

  // Check for security schemes
  if (spec.security && spec.security.length > 0) {
    validateSecurity(spec, { errors, warnings, strict });
  }

  // Strict mode validations
  if (strict) {
    performStrictValidations(spec, { errors, warnings });
  }
}

/**
 * Validates paths section
 */
async function validatePaths(
  paths: OpenAPIV3.PathsObject,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
    strict?: boolean;
  }
): Promise<void> {
  const { errors, warnings } = context;

  for (const [pathName, pathItem] of Object.entries(paths)) {
    if (!pathItem) continue;

    // Validate path parameters
    if (pathName.includes('{') && pathName.includes('}')) {
      const pathParams = pathName.match(/\{([^}]+)\}/g);
      if (pathParams) {
        for (const param of pathParams) {
          const paramName = param.slice(1, -1);
          if (!paramName) {
            errors.push({
              path: `paths.${pathName}`,
              message: 'Empty path parameter found',
              code: 'invalid_path_parameter',
              severity: 'error'
            });
          }
        }
      }
    }

    // Validate operations
    const operations = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'];
    for (const method of operations) {
      const operation = pathItem[method as keyof OpenAPIV3.PathItemObject] as OpenAPIV3.OperationObject | undefined;
      if (operation) {
        validateOperation(operation, pathName, method, { errors, warnings });
      }
    }
  }
}

/**
 * Validates a single operation
 */
function validateOperation(
  operation: OpenAPIV3.OperationObject,
  path: string,
  method: string,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
  }
): void {
  const { errors, warnings } = context;
  const operationPath = `paths.${path}.${method}`;

  // Check operation ID
  if (!operation.operationId) {
    warnings.push({
      path: `${operationPath}.operationId`,
      message: 'Operation ID is missing - will generate one automatically',
      code: 'missing_operation_id'
    });
  } else {
    // Validate operation ID format
    if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(operation.operationId)) {
      warnings.push({
        path: `${operationPath}.operationId`,
        message: 'Operation ID should start with a letter and contain only letters, numbers, and underscores',
        code: 'invalid_operation_id_format'
      });
    }
  }

  // Check summary and description
  if (!operation.summary && !operation.description) {
    warnings.push({
      path: `${operationPath}`,
      message: 'Operation should have either a summary or description',
      code: 'missing_operation_docs'
    });
  }

  // Validate parameters
  if (operation.parameters) {
    operation.parameters.forEach((param, index) => {
      if ('$ref' in param) return; // Skip referenced parameters for now

      const parameter = param as OpenAPIV3.ParameterObject;
      if (!parameter.name) {
        errors.push({
          path: `${operationPath}.parameters[${index}].name`,
          message: 'Parameter name is required',
          code: 'missing_parameter_name',
          severity: 'error'
        });
      }

      if (!parameter.in) {
        errors.push({
          path: `${operationPath}.parameters[${index}].in`,
          message: 'Parameter location (in) is required',
          code: 'missing_parameter_location',
          severity: 'error'
        });
      }
    });
  }

  // Validate responses
  if (!operation.responses) {
    errors.push({
      path: `${operationPath}.responses`,
      message: 'Operation must define at least one response',
      code: 'missing_responses',
      severity: 'error'
    });
  } else {
    const hasSuccessResponse = Object.keys(operation.responses).some(
      code => code.startsWith('2') || code === 'default'
    );

    if (!hasSuccessResponse) {
      warnings.push({
        path: `${operationPath}.responses`,
        message: 'Operation should define at least one success response (2xx)',
        code: 'missing_success_response'
      });
    }
  }
}

/**
 * Validates components section
 */
async function validateComponents(
  components: OpenAPIV3.ComponentsObject,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
    strict?: boolean;
  }
): Promise<void> {
  const { warnings } = context;

  // Check for unused schemas
  if (components.schemas) {
    const schemaNames = Object.keys(components.schemas);
    if (schemaNames.length > 0) {
      // This is a simplified check - in a full implementation, 
      // we would track which schemas are actually referenced
      warnings.push({
        path: 'components.schemas',
        message: `Found ${schemaNames.length} schema definitions`,
        code: 'schema_info'
      });
    }
  }

  // Check security schemes
  if (components.securitySchemes) {
    const schemeNames = Object.keys(components.securitySchemes);
    warnings.push({
      path: 'components.securitySchemes',
      message: `Found ${schemeNames.length} security scheme(s): ${schemeNames.join(', ')}`,
      code: 'security_schemes_info'
    });
  }
}

/**
 * Validates security configuration
 */
function validateSecurity(
  spec: OpenAPIV3.Document,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
    strict?: boolean;
  }
): void {
  const { errors, warnings } = context;

  if (!spec.components?.securitySchemes) {
    errors.push({
      path: 'security',
      message: 'Security requirements defined but no security schemes found in components',
      code: 'missing_security_schemes',
      severity: 'error'
    });
    return;
  }

  // Validate that all security requirements reference valid schemes
  spec.security?.forEach((requirement, index) => {
    Object.keys(requirement).forEach(schemeName => {
      if (!spec.components?.securitySchemes?.[schemeName]) {
        errors.push({
          path: `security[${index}]`,
          message: `Security scheme "${schemeName}" is not defined in components.securitySchemes`,
          code: 'undefined_security_scheme',
          severity: 'error'
        });
      }
    });
  });
}

/**
 * Performs strict mode validations
 */
function performStrictValidations(
  spec: OpenAPIV3.Document,
  context: {
    errors: ValidationResult['errors'];
    warnings: ValidationResult['warnings'];
  }
): void {
  const { warnings } = context;

  // Check for deprecated operations
  if (spec.paths) {
    for (const [pathName, pathItem] of Object.entries(spec.paths)) {
      if (!pathItem) continue;

      const operations = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'];
      for (const method of operations) {
        const operation = pathItem[method as keyof OpenAPIV3.PathItemObject] as OpenAPIV3.OperationObject | undefined;
        if (operation?.deprecated) {
          warnings.push({
            path: `paths.${pathName}.${method}`,
            message: 'Operation is marked as deprecated',
            code: 'deprecated_operation'
          });
        }
      }
    }
  }

  // Check for missing examples
  warnings.push({
    path: 'root',
    message: 'Consider adding examples to improve API documentation',
    code: 'missing_examples'
  });
}