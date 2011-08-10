import java.util.HashMap;
import java.util.Map;


public class TokenDictionary {
  final Map<String,Integer> tokenToIdx = new HashMap<String,Integer>();
  final Map<Integer,String> idxToToken = new HashMap<Integer,String>();
  private int tokenIdx = 0;

  public int idxForToken(String token) {
    token = token.trim();
    if (tokenToIdx.containsKey(token)) {
      return tokenToIdx.get(token);      
    }
    else {
    	tokenToIdx.put(token, tokenIdx);
      idxToToken.put(tokenIdx, token);
      return tokenIdx++;
    }
  }

  public String tokenForIdx(int idx) {
    return idxToToken.get(idx);
  }

  public String prettyEdgeForIdxs(int idx1, int idx2) {
    return "[" + tokenForIdx(idx1) + "] -> [" + tokenForIdx(idx2) + "]";
  }

  public String outputEdgeForIdxs(int idx1, int idx2) {
    return tokenForIdx(idx1) + "\t" + tokenForIdx(idx2);
  }
  
}
