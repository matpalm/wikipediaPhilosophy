import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

public class DistanceToPhilosophy {
  
  private final Map<String,Integer> tokenToIdx = new HashMap<String,Integer>();
  private final Map<Integer,String> idxToToken = new HashMap<Integer,String>();
  private int tokenIdx = 0;
  private final String startNode;
  
  private Map<Integer,List<Integer>> edges = new HashMap<Integer,List<Integer>>();
  
  public static void main(String s[]) throws IOException {
    new DistanceToPhilosophy(s[0]).go();
  }
  
  public DistanceToPhilosophy(String startNode) {
    this.startNode = startNode;
  }
  
  public void go() throws IOException {
    parseInputFile();
    breadthFirstWalk();    
  }

  private void parseInputFile() throws FileNotFoundException, IOException {
    BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
    String next;    
    int linesProcessed=0;
    
    while((next=reader.readLine())!=null) {
      
      String[] cols = next.split("\t");
      // note: we want the reverse graph
      int toNode = tokenForIdx(cols[0]);
      int fromNode = tokenForIdx(cols[1]);          
      
      if (edges.containsKey(fromNode)) {
        List<Integer> outboundEdges = edges.get(fromNode);
        if (outboundEdges.contains(toNode)) {
          System.err.println("already and edge from "+fromNode+" ("+idxToToken.get(fromNode)+") to "+toNode+" ("+idxToToken.get(toNode)+")");
        } 
        else {
          outboundEdges.add(toNode);
        }         
      }
      else {        
        List<Integer> newSetOfEdges = new ArrayList<Integer>();
        newSetOfEdges.add(toNode);
        edges.put(fromNode, newSetOfEdges);
      }
      
      if ((++linesProcessed % 1000)==0) {
        System.err.println("slurp input; processed "+linesProcessed);
      }

    }
    
    if (!tokenToIdx.containsKey(startNode)) {
      throw new RuntimeException("after parsing stdin never saw starting node ["+startNode+"]");
    }
  }

  private void breadthFirstWalk() {
    Queue<Integer> boundary = new LinkedList<Integer>();
    boundary.add(tokenToIdx.get(startNode));
    int distance = 0;    
    while(boundary.size() != 0) {
      Queue<Integer> frontier = new LinkedList<Integer>();
      for(int edge : boundary) {
        System.out.println(idxToToken.get(edge) + "\t" + distance);
        if (edges.containsKey(edge)) {
          frontier.addAll(edges.get(edge));
        }
      }
      System.err.println("distance="+distance+" frontier size "+frontier.size());
      distance++;
      boundary = frontier;      
    }
  }
  
  public int tokenForIdx(String token) {
    // build token -> idx
    if (tokenToIdx.containsKey(token)) {
      return tokenToIdx.get(token);      
    }
    else {
      tokenToIdx.put(token, tokenIdx);
      idxToToken.put(tokenIdx, token);
      return tokenIdx++;
    }
  }
}
