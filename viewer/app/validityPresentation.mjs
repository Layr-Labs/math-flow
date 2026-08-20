/**
 * Return the two validity-v3 reference sets that must remain visually distinct.
 * A missing required-dependency field identifies a legacy validity-v2 assessment.
 */
export function validityReferenceGroups(judgment, assessment) {
  const required = assessment?.requiredDependencyTransactionIds;
  const declared = judgment?.declaredReferenceTransactionIdsByClaim?.[assessment?.claimKey];
  if (!Array.isArray(required) || !Array.isArray(declared)) return null;
  return {
    declaredReferenceTransactionIds: declared,
    requiredDependencyTransactionIds: required,
  };
}
